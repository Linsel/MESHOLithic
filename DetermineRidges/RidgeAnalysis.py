from util import *

# currentdir = os.getcwd()
# parentdir = os.path.dirname(currentdir)
# sys.path.insert(0, parentdir) 


# import numpy as np
# import pandas as pd


# import inspect
# import itertools
# from plyfile import PlyData,PlyElement
# import logging

import networkx as nx

from Classes.BasicClasses import Mesh,Pline,manualEdges
from Functions.EssentialDecorators import timing
from Functions.PolylineGraph import get_cycle
from Functions.EssentialGraphFunctions import get_basic_graph_properties
from Functions.exportFiles.writeTxt import write_labels_txt_file

# from IntegralInvariants.II1DClasses import MSIIPline
# kMeans
from sklearn.cluster import KMeans
from scipy.spatial import distance

# import functions to alter meshes  
from Functions.EssentialMeshAlteration import find_vertices_within_radius,get_nearest_neighbor,create_label_submeshes, get_submesh_quality
from Functions.EssentialLabelAlteration import get_unique_labels,get_uniquelabel_vertlist,get_labels_IoU_max,get_labels_IoU,label_vertices

# import functions to export pline file
from Functions.PlineExport import exp_pline, exp_pline_funcvals

from Functions.BasicMSII1D import angle_between_vectors

# Functions for creating 3D shaped connections of graph models
from Functions.Essential3DPlotting import create_node_sphere,create_rotated_connection

# handeling of labelled meshes, extracting the outline 
class LabelledMesh (Mesh):

    """
    The LabelledMesh object is a child object of Mesh object and parent object of Polylines and PolylineGraphs objects.
    """

    def __init__(   self,           
                    labelfilepath: str = None):

        """
        Super initialize Mesh object which contains a triangular 3D mesh and expand this with a label file.

        Args:   
            labelfilepath (str): path to the label txt file        
        """

        super().__init__()

        # check for None only to avoid warning messages in subclasses
        if labelfilepath is not None:
            self.labelfilepath = labelfilepath                

    def load_labelled_mesh (self, 
                            path: str, 
                            id: str, 
                            preprocessed: str, 
                            labelfilepath: str):

        """
        Function to load a ply file and the txt label file to the LabelledMesh object
        
        Args:
            path (str): String representing the path to the file.
            id (str): String representing the file id of the ply file.
            preprocessed (str): String representing the preprocessing step of the ply file.    
            labelfilepath (str): name of the label file                 
        """
        
        self.load_ply(path, id, preprocessed)

        # path to label file 
        self.labelfilepath = labelfilepath 

        self.read_label_as_dict()    
        
    # Import faces and vertices of ply as numpy arrays
    def read_label_as_dict (self):

        """
        Imports the label txt file of an ply file            
        """        


        # import label and create dictionary 
        df_label = pd.read_csv(self.labelfilepath,skiprows=5,header=None,sep=' ',names=['a','b'],dtype=int)  

        self.dict_label = dict(zip(df_label.a, df_label.b))

        self.unique_labels = get_unique_labels(self.dict_label)

    def extract_ridges (self):   

        """
        Detects ridges and centroids of labelled areas on the surface of the labeledMesh object.
        Goal is extracting the outline vertices of each label.
        """

        # Create a dictionary of all vertices (keys), which have more than 1 neighbouring label and a list of all neighbouring vertices with the same label 
        
        self.ridge_neighbour_shared_label = {   key:
                                                    [(v) for v in self.vertex_neighbors_dict[key] + [self.dict_label[key]] 
                                                            if self.dict_label[key] == self.dict_label[v]]
                                                
                                                for key, v in enumerate(self.vertices) 
                                                        if len(np.unique([self.dict_label[v] 
                                                            for v in self.vertex_neighbors_dict[key]] + [self.dict_label[key]])) > 1
                                            }

        # Create a dictionary of all labels (keys) and a set of vertices with the same label (values), which belong to the ridge_neighbour_shared_label dictionary
        self.label_outline_vertices =   {label: {r_vert
                                                    for r_vert in self.ridge_neighbour_shared_label.keys()
                                                    if self.dict_label[r_vert] == label
                                                }

                                            for label in self.unique_labels
                                        }

        # Create a dictionary of all labels (keys) and a set of edges, where each vertex have vertices with the same label (values)  
        self.label_outline_edges = {label:  {(val,va) 
                                             
                                                for val in values 
                                                    for va in self.ridge_neighbour_shared_label[val]

                                                if  va in self.ridge_neighbour_shared_label.keys() and 
                                                    val in self.ridge_neighbour_shared_label.keys()
                                            }

                                        for label,values in self.label_outline_vertices.items()            
                                    }    

    # preprocessing 
    def prep_ridges(self):

        """
        Prepares ridge-related structures for further processing.

        This method performs several operations related to 'ridges' in the context of lithic artifacts as border between adjacent scars.
        Also creates dictionary of neighboring labels and derives from that a set of edges for a graph representation.                 
        
        Attributes:
            ridge_neighbour_notshared_label (dict): dictionary with vertices (keys) and neighboring vertices with different label (values).

            neighbouring_labels (dict): dictionary with labels (keys) and neighboring labels (values). 

            neighbouring_labels_set (set): A set of tuples (edges) of neighboring labels, creating a set of bidiretional edges for graph. 
        """

        # identifies border vertices between labels.
        self.ridge_neighbour_notshared_label = {key: {self.dict_label[v] for v in self.vertex_neighbors_dict[key] + [self.dict_label[key]] 
                                                if self.dict_label[key] != self.dict_label[v]}
                                                
                                        
                                        for key, v in enumerate(self.vertices) 
                                                if len(np.unique([self.dict_label[v] 
                                                    for v in self.vertex_neighbors_dict[key]] + [self.dict_label[key]])) > 1
                                            }                                                

        # identifies neighboring labels
        self.neighbouring_labels =   {ul: {self.dict_label[r_vert]
                                                for r_vert,labels in self.ridge_neighbour_notshared_label.items()
                                                for label in labels
                                                if self.dict_label[r_vert] != label and 
                                                ul == label
                                            }

                                        for ul in self.unique_labels
                                    }
        
        # create set of neighboring labels
        self.neighbouring_labels_set =   {(label,n_l)
                                            for label,neigh_labels in self.neighbouring_labels.items()
                                                for n_l in neigh_labels
                                        }           
        
    def get_centroids (self):

        """
        Creates a dictionary containing labels (key) and centroid of label outline vertices (values). 
        """

        # 
        self.centroids =    {label:np.mean([self.vertices[v] 
                                                for v in verts],axis=0)

                                for label, verts in self.label_outline_vertices.items()        
                            }

    def get_NNs (self):

        """
        Creates two dictionaries of containing both labels (keys) and 

            -   nearest neighbor of the label centroid to complete mesh or 
            -   nearest neighbor of the label centroid to its label submesh 
                
            as vertex coordinates (values).
        """

        # Nearest neighbour (NN) from label centroid to mesh        
        self.NNs_to_mesh = {label: get_nearest_neighbor(self.kdtree,
                                                        self.vertices,
                                                        centroid)
                                
                                for label, centroid in self.centroids.items()
                            }

        # Nearest neighbour (NN) from label centroid to submesh 
        self.NNs_to_submeshes = {label: get_nearest_neighbor(self.submeshes[label][0].kdtree,
                                                             self.submeshes[label][0].vertices,
                                                             centroid)
                                
                                    for label, centroid in self.centroids.items()
                                } 

    def get_NNs_ids (self):

        """
        Creates a dictionary containing labels (key) and nearest neighbor to label centroid as vertex id (values). 
        """

        # Nearest neighbour (NN) from label centroid to submesh        
        self.NNs_ids = {} 
                                
        for label, centroid in self.centroids.items():

            _,index = self.kdtree.query(centroid)

            self.NNs_ids [label] = index

    ## handelling of labelfile
    def get_label_submeshes (self):

        """
        Splits mesh in submeshes according to imported labels.
        """        

        labels = get_uniquelabel_vertlist (self.dict_label)

        tri_mesh = trimesh.load(''.join([self.path, self.id, self.preprocessed, '.ply']))

        # Creates a dictionary of with a ridge point and the neighbours with the same label
        self.submeshes = create_label_submeshes (tri_mesh,labels)

        del tri_mesh

    ######################
    # create two submeshes passed on kmeans-clustering 
    def get_front_and_back_kmeans (self): 

        """
        Detects front and back of a two-sided mesh.

        Attributes:
            kmeans (sklearn.cluster.KMeans):    A fitted sklearn.cluster.KMeans object with two clusters
                                                and random_state=0.
            klabels (list): An extra stored kmeans.labels_ attribute of the kmeans object.

        """           

        # Get normal directions
        self.kmeans = KMeans(n_clusters=2, random_state=0).fit(self.normals)
        self.klabels = {vert:label + 1 for vert,label in enumerate(self.kmeans.labels_)} 

    def export_kmeans_labels (self):

        """
        Creates from the kmeans labels a txt file
        """

        clust_verts = get_labels_IoU_max (self.dict_label,self.klabels) 

        clust_labels = {val:ul for ul,values in clust_verts.items() for val in values}

        write_labels_txt_file (clust_labels, ''.join ([ self.path, 
                                                        self.id,
                                                        '_'.join([  '',
                                                                    'Kmeans-labels'])
                                                        ]))

    def kmeans_slice (self):
        """
        Slices mesh based on IoU_max of the k-means clustering and exports submeshes.

        """

        clust_verts = get_labels_IoU_max (self.dict_label,self.klabels) 

        clust_labels = {ul:{i:self.dict_label[n] for i,n in enumerate(values)} for ul,values in clust_verts.items()}

        tri_mesh = trimesh.load(''.join([self.path, self.id, self.preprocessed, '.ply']))

        submeshes = create_label_submeshes(tri_mesh,clust_verts)

        del tri_mesh

        for clust,submesh in submeshes.items():
            if submesh [0]:

                submesh[0].export(''.join ([self.path, 
                                                    self.id,
                                                    '_',
                                                    '-'.join(['Kmeans',
                                                            'cl',
                                                            str(clust)]),                                          
                                                    '.ply']),
                                                    file_type='ply')
                
                
                write_labels_txt_file (clust_labels[clust], ''.join ([self.path, 
                                                    self.id,
                                                    '_',
                                                    '-'.join(['Kmeans',
                                                            'cl',
                                                            str(clust)]),
                                                    '-labels']))
       
    # create meshes for exporting
    ## ridges mesh
    def create_ridges_mesh(self):

        """
        Creates a mesh of the label outlines. 

        """   
        
        face_set = [set(list(face)) for face in self.faces]     

        renumbered_ridge_id = {key:n for n,key in enumerate(self.ridge_neighbour_shared_label.keys())}

        ridge_neighbour_shared_label_set =  set(self.ridge_neighbour_shared_label.keys())

        faces_temp = [face for face in face_set if face.issubset(ridge_neighbour_shared_label_set)]

        faces_list = [[renumbered_ridge_id[vert] for vert in face] for face in faces_temp]

        faces_array = np.array(faces_list)

        vertex_data = np.array([list(self.vertices[key]) for key in self.ridge_neighbour_shared_label.keys()])
        
        self.ridges_mesh = trimesh.Trimesh(vertices=vertex_data,faces=faces_array)

        self.ridge_labels = {n_vert:1 for n_vert,_ in enumerate(vertex_data)}

    ## nodes mesh
    def create_nodes_mesh (self,nodes,radius):

        self.nodes_list = [create_node_sphere (self.centroids [node],radius) for node in nodes]

        self.nodes_mesh = trimesh.util.concatenate(self.nodes_list)

        self.node_labels = {n_vert: n + 1 for n,node in enumerate(nodes) for n_vert,_ in enumerate(create_node_sphere (self.centroids [node],radius).vertices)}


    ## get mean quality of submeshes 
    def get_submeshes_quality_mean (self):

        self.vertlist = get_uniquelabel_vertlist (self.dict_label)

        self.get_quality ()

        self.submeshes_quality = {label: get_submesh_quality(self.quality,vertlist)
                                    for label,vertlist in self.vertlist.items()
                                }

        submeshes_quality_mean = {label:np.mean(vals)
                    for label,submesh in self.submeshes_quality.items() 
                        for vals in submesh.values()
                }
        
        return submeshes_quality_mean

# creates multiple graph models for analysing the ridges
class PolylineGraphs (LabelledMesh):

    """
    The Polylines object is a child object of the Pline and LabelledMesh objects.
    """

    def __init__(self) -> object:

        """
        Super initialize Pline and LabelledMesh object to get their functions and arguments.
        """    

        super().__init__()

    def prep_polygraphs(self,
                        path: str, 
                        id: str, 
                        preprocessed: str, 
                        labelfilepath: str):
    
        """
        Function to prepare a polygraph from labbeled mesh.
        
        Args:
            path (str): String representing the path to the file.
            id (str): String representing the file id of the ply file.
            preprocessed (str): String representing the preprocessing step of the ply file.    
            labelfilepath (str): path to the label file                   
        """  

        self.load_labelled_mesh (path, id, preprocessed, labelfilepath)

        self.extract_ridges()
        # create node coordinates
        self.get_centroids()        

        # self.get_NNs()
              
    def edges_to_polygraphs (self):

        """
        Converts outline edges of all labels to separete graphs in a dictionary.

        Attributes:
            polygraphs (dict): dictionary of labels (keys) and their graphs of all outline vertices (values). 

        """   
    
        self.polygraphs = {}

        for label,values in self.label_outline_edges.items():
            
            # Create an empty graph
            G = nx.Graph()

            # Add nodes and edges from the list of tuples
            for edge in values:
                G.add_nodes_from(edge, label=label)
                G.add_edge(*edge)

            self.polygraphs[label] = G

        # self.polygraphs = polygraphs

    def polygraphs_to_polylines(self):

        """
        Converts polygraphs to polylines and identifies labels without cycles.

        Attributes:
            polylines (dict): dictionary containing labels (keys) and polylines structures derived from the polygraphs.
            no_polyline (list): A list of labels for which no closed polyline (cycle) could be identified.
            label_outline_vertices (dict): A dictionary from which labels with no cycles are removed.

        """     

        self.polylines = {}

        # list to save all labels, which have no cycle
        self.no_polyline = []
        i = 1

        for label,G in self.polygraphs.items():

            # connected_components = get_connected_components (G)

            # for cc in connected_components:
            #     G_temp  = nx.Graph()
            #     edges = nx.edges(G, cc)
                
            #     for edge in edges:
            #         G_temp.add_nodes_from(edge, label=label)
            #         G_temp.add_edge(*edge)

            try:       
                polyline,_ = get_cycle(G)

                    
                self.polylines[label] = polyline

            except:

                del self.label_outline_vertices[label] 

                self.no_polyline.append(label)

                logging.info(' '.join(['The label',str(label),'has no cycle']))

            i += 1

    def get_connected_components(self):
        """
        Identifies and stores connected components in the graph_polyline.

        Attributes:
            ccs (list): list of vertices representing a connected component in the graph_polyline.
        """

        connected_components = nx.connected_components(self.graph_polyline)

        self.ccs = [list(cc) for cc in connected_components]

    # preparing data for creating a pline text file 
    ## collecting the data necessary to create the header 
    def create_dict_mesh_info(self):

        """
        Creates a dictionary with basic information about the mesh.

        Attributes:
            dict_mesh_info (dict): A dictionary containing:
                - 'Mesh': ID of the mesh.
                - 'Vertices': number of vertices of the mesh.
                - 'Faces':  number of faces of the mesh.
                - 'Polylines': number of polylines in the polyline file.

        """

        self.dict_mesh_info =   {
                                'Mesh' :    self.id,
                                'Vertices': len(self.pline_vertices.keys()),
                                'Faces' :   len(self.faces),
                                'Polylines':len(self.polylines)
                                }
    
    ## collecting coordinates and normals of polyline vertices data necessary 
    def create_normals_vertices (self):

        """
        Collects coordinates and normals of polyline vertices.

        Attributes:
            pline_vertices (dict): dictionary containing vertex indices of all vertices belonging to a polyline (keys) and their coordinates (values).
            pline_normals (dict): dictionary containing vertex indices of all vertices belonging to a polyline (keys) and their normals (values).
        """        
        
        self.pline_vertices = {}
        self.pline_normals = {}

        for polyline in self.polylines.values():    
            
            for n,vertex in enumerate(polyline):
                self.pline_vertices[n] = self.vertices[vertex]
                self.pline_normals[n] = self.normals[vertex]
                 
    def prepare_polyline (self):

        """
        Prepares a dictionary with information for each polyline.

        Attributes:
            dict_plines (dict): dictionary containing polyline indices (keys), and a nested dictionary containing: 
                'label_id': label of polyline.
                'vertices': vertices belonging to polyline.
                'vertices_no': number of vertices of polyline.
        """        

        self.dict_plines = {n:{   
                                'label_id':self.polygraphs[n].nodes[polyline[0]]['label'],
                                'vertices':  polyline,
                                'vertices_no':  len(polyline),
                                }
                                    for n,polyline in self.polylines.items()
                                }     
        

    @timing
    def ridge_pairs(self):


        self.ridges_pairs = {}
        self.ridges_pairs_max = {}        
        self.ridges_pairs_min = {} 

        for edge in self.neighbouring_labels_set:
            if (edge[1],edge[0]) not in self.ridges_pairs:

                
                try:

                    difference = self.mean_segments_funv[(edge[0],edge[1])] - self.mean_segments_funv[(edge[1],edge[0])]

                    self.ridges_pairs [(edge[0],edge[1])] = {'paired_scar':(edge[1],edge[0]),
                                                            'bigger_smaller': np.sign(difference), 
                                                            'difference' : np.absolute(difference)}
                    
                    difference_max = self.mean_maxsegments_funv[(edge[0],edge[1])] - self.mean_maxsegments_funv[(edge[1],edge[0])]

                    self.ridges_pairs_max [(edge[0],edge[1])] = {'paired_scar':(edge[1],edge[0]),
                                                            'bigger_smaller': np.sign(difference_max), 
                                                            'difference' : np.absolute(difference_max)}
                    

                    difference_min = self.mean_minsegments_funv[(edge[0],edge[1])] - self.mean_minsegments_funv[(edge[1],edge[0])]

                    self.ridges_pairs_min [(edge[0],edge[1])] = {'paired_scar':(edge[1],edge[0]),
                                                            'bigger_smaller': np.sign(difference_min), 
                                                            'difference' : np.absolute(difference_min)}

                except:
                    continue        

    def export_pline(self):

        """       
        Export of Pline as pline file according to the GigaMesh Polyline Standard.
        """        

        exp_pline(self.path, self.id, self.dict_mesh_info, self.dict_plines, self.pline_vertices, self.pline_normals)

    def export_pline_funcvals(self,
                        funcvals: dict,
                        var_name: str):
        """
        Exports polyline function values as a text file following the GigaMesh Polyline Standard.

        Args:    
            funcvals (dict): vertex:functionvalue dictionary, e.g. MSII curvature
            var_name (str): Name of the passed function value, e.g. 'MSII'.
        """   

        exp_pline_funcvals(self.path, self.id, self.dict_mesh_info, funcvals, var_name)

    # segmentate polyline 
    def polineline_segmenting(self):

        """
        Segments each polyline based on neighboring labels and assigns to edge.

        Attributes:
            segments (dict): dictionary consisting of edge tuples of labels (keys) and a nested dictionary. 
                                This contains 'vertices' (key) and vertex ids belonging to segment (values).
        """        
      
        self.segments = { 
                    (label,n_l):    
                        {'vertices':[ v
                                        for v in self.dict_plines[label]['vertices'] 
                                            if n_l in self.ridge_neighbour_notshared_label[v]]}

                    for label,neigh_labels in self.neighbouring_labels.items()
                    for n_l in neigh_labels
                    if n_l in self.neighbouring_labels[label]
                }    

    def  segments_export (self):

        self.segments



    def segment_pline_funct_val (self,
                                 funct_val:dict):

        """
        Segments polylines and assigns function values to dictionary.

        Args:
            funct_val (dict): dictionary containing vertex ids (keys) and function values (values).

        Attributes:
            segments_funv (dict): dictionary consisting of edge tuples of labels (keys) and a nested dictionary. 
                                This contains 'vertices' (key) and function values of vertices belonging to segment (values).        
        """        

        self.polineline_segmenting () 

        self.segments_funv = { 
                    (label,n_l):    
                        {'funct_vals':[ funct_val[v]
                                        for v in self.dict_plines[label]['vertices'] if n_l in self.ridge_neighbour_notshared_label[v]]}

                    for label,neigh_labels in self.neighbouring_labels.items()
                    for n_l in neigh_labels
                    if n_l in self.neighbouring_labels[label]
                }

    def segment_to_graph(self):

        """
        Converts polyline segments into a ridge graph.

        Attributes:
            G_ridges (nx.Graph): graph representing the segments ('edges': segment ids, 
                                'nodes': vertices, 'length': number of vertices)
        """        

        self.G_ridges = nx.Graph()    

        for edge,nodes in self.segments.items():
            if nodes != {'vertices': []}:

                self.G_ridges.add_nodes_from(edge)
                self.G_ridges.add_edge(*edge,
                                                nodes = nodes['vertices'],
                                                length = len(nodes['vertices']))
            else:
                continue

    def get_directed_edges( self,
                            ridge_pairs:dict):

        """
        Determines direction of edges based on differences between function values.

        Args:
            ridges_pairs (dict): dictionary containing edges as tuples (keys) and nested dictionary derived from mean segment values with 3 keys:
                                    - 'paired_scar' :   reversed ordered edge (tuple)
                                    - 'bigger_smaller': sign of difference. 
                                    - 'difference':     difference between func values between vertices belonging to edge[0] and edge[1]. 
                                                        Note: Due to the adjacency of labels, segments consist of borders of two labels at once. 
                                     

        Returns:
            directed_edges (dict): dictionary of directed edges with their respective absolut differences.
        """        

        directed_edges = dict( [(r1,values['difference'] )
                                        for r1,values in ridge_pairs.items() 
                                            if values['bigger_smaller'] == -1.0] + 
                                    [(values['paired_scar'],values['difference'])  
                                        for values in ridge_pairs.values()
                                            if values['bigger_smaller'] == 1.0])
        # directed_edges = {( r1 if values['bigger_smaller'] == -1.0 else values['paired_scar']):values['difference'] 
        #                         for r1,values in ridge_pairs.items()}
        return directed_edges

    def create_directed_ridgegraph(self,
                                   ridge_pairs:dict):

        """
        Creates a directed ridge graph from ridge pairs.

        Args:
            ridges_pairs (dict): dictionary containing edges as tuples (keys) and nested dictionary derived from mean segment values with 3 keys:
                                    - 'paired_scar' :   reversed ordered edge (tuple)
                                    - 'bigger_smaller': sign of difference. 
                                    - 'difference':     difference between mean func values between vertices belonging to edge[0] and edge[1]. 
                                                        Note: Due to the adjacency of labels, segments consist of borders of two labels at once. 
                                                         

        Returns:
            (nx.DiGraph): directed graph representing the ridge pairs with weights.
        """        
        

        directed_edges = self.get_directed_edges(ridge_pairs)
        
        DiG_ridges = nx.DiGraph()

        for edge,difference in directed_edges.items():
            DiG_ridges.add_nodes_from(edge)
            DiG_ridges.add_edge(*edge,weight = difference)

        return DiG_ridges

    def label_connections_nodes (self):

        """
        Creates labels for vertices belonging to the undirected representation of the scar-ridge graph model in 3D. 
        """        

        # creates label text file for the undirected models of the edges (connection) between the scars (nodes)
        label_vertices( self,
                        0,
                        self.connections_mesh.vertices,
                        [num for num,_ in enumerate(self.G_ridges.edges, 1)], 
                        '_connections')

        # creates label text file for the undirected models of the scars (nodes)
        label_vertices( self, 
                        len(self.connections_mesh.vertices),
                        self.nodes_mesh.vertices,
                        [num for num,_ in enumerate(self.G_ridges.nodes, 1)],
                        '_nodes')

    def direct_ridgegraph(self):

        """
        Creates directed ridge graphs for different types of ridge pairs.

        Constructs directed graphs for normal, maximum, and minimum ridge pairs.
        
        Attributes:
            DiG_ridges (dict): dictionary of directed graphs (values) for different types (keys) of ridge pairs.
                'min':      DiG_ridges based on the difference of the minimum function values between adjacent nodes.  
                'normal':   DiG_ridges based on the difference of the mean function values between adjacent nodes.  
                'max':      DiG_ridges based on the difference of the maximum function values between adjacent nodes.                                    

        """        

        self.DiG_ridges = {}

        self.DiG_ridges ['min']  = self.create_directed_ridgegraph(self.ridges_pairs_min)         

        self.DiG_ridges ['normal'] = self.create_directed_ridgegraph(self.ridges_pairs) 

        self.DiG_ridges ['max']  = self.create_directed_ridgegraph(self.ridges_pairs_max) 


    def get_DiG_ridge_properties(self,
                                 graphname:str):  

        """
        Retrieves basic properties of a specified directed ridge graph.

        Args:
            graphname (str): The name of the directed ridge graph type.

        Attributes:
            DiG_properties (dict): dictionary containing edges (keys) and basic properties ('degree','degree_weigthed','betweenness_centrality') 
            of the undirected ridge graph (values). 
        """             

        self.DiG_properties = get_basic_graph_properties(self.DiG_ridges [graphname])

    def get_G_ridge_properties(self):

        """
        Retrieves basic properties of the undirected ridge graph.

        Attributes:
            G_properties: dictionary containing edges (keys) and basic properties ('degree','degree_weigthed','betweenness_centrality') 
            of the undirected ridge graph (values).
        """        

        self.G_properties = get_basic_graph_properties(self.G_ridges)

    def export_DiG_node_properties(self):

        """
        Exports the node properties of the directed ridge graph.

        This method extracts and exports various node properties (degree, weighted degree, betweenness centrality) of the directed 
        ridge graphs to text files.

        Note:
            - Exports are saved with specific naming conventions based on the graph type and a radius parameter (`self.nrad`).
        """        

        DiG_node_degree = {key:self.DiG_properties[val]['degree'] 
                           for key,val in self.dict_label.items() if val not in self.no_polyline}

        DiG_node_degree_weighted = {key:self.DiG_properties[val]['degree_weigthed'] 
                                    for key,val in self.dict_label.items() if val not in self.no_polyline}

        DiG_node_betweenness = {key:self.DiG_properties[val]['betweenness_centrality'] 
                                for key,val in self.dict_label.items() if val not in self.no_polyline}

        write_labels_txt_file (DiG_node_degree, ''.join([self.path, self.id, '_DiG-node_degree',str(self.nrad)]))

        write_labels_txt_file (DiG_node_degree_weighted, ''.join([self.path, self.id, '_DiG-node_degree_weighted',str(self.nrad)]))

        write_labels_txt_file (DiG_node_betweenness, ''.join([self.path, self.id, '_DiG-node_betweenness',str(self.nrad)]))

    def export_G_node_properties(self):

        """
        Exports the node properties of the directed ridge graph.

        This method extracts and exports various node properties (degree, weighted degree, betweenness centrality) of the directed 
        ridge graphs to text files.

        Note:
            - Exports are saved with specific naming conventions based on the graph type and a radius parameter (`self.nrad`).
        """        

        G_node_degree = {key:self.G_properties[val]['degree'] 
                         for key,val in self.dict_label.items() if val not in self.no_polyline}

        G_node_degree_weighted = {key:self.G_properties[val]['degree_weigthed'] 
                                  for key,val in self.dict_label.items() if val not in self.no_polyline}

        G_node_betweenness = {key:self.G_properties[val]['betweenness_centrality'] 
                              for key,val in self.dict_label.items() if val not in self.no_polyline}

        write_labels_txt_file (G_node_degree, ''.join([self.path, self.id, '_G-node_degree',str(self.nrad)])) 

        write_labels_txt_file (G_node_degree_weighted, ''.join([self.path, self.id, '_G-node_degree_weighted',str(self.nrad)]))    
        
        write_labels_txt_file (G_node_betweenness,''.join([self.path, self.id, '_G-node_betweenness',str(self.nrad)]))  
