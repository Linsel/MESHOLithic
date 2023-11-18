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
from Functions.EssentialMeshAlteration import find_vertices_within_radius,get_nearest_neighbor,create_label_submeshes 
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
                    label_name: str = None):

        """
        Super initialize Mesh object which contains a triangular 3D mesh and expand this with a label file.

        Args:   
            label_name (str): name of the label txt file        
        """

        super().__init__()

        # check for None only to avoid warning messages in subclasses
        if label_name is not None:
            self.label_name = label_name                

    def load_labelled_mesh (self, 
                            path: str, 
                            id: str, 
                            preprocessed: str, 
                            label_name: str, 
                            exp_path: str = ''):

        """
        Function to load a ply file and the txt label file to the LabelledMesh object
        
        Args:
            path (str): String representing the path to the file.
            id (str): String representing the file id of the ply file.
            preprocessed (str): String representing the preprocessing step of the ply file.    
            label_name (str): name of the label file        
            exp_path (str): String representing the export folder where to save all derived data.                
        """
        self.load_ply(path, id, preprocessed, exp_path)

        self.label_name = label_name
        self.read_label_as_dict()       

    # Import faces and vertices of ply as numpy arrays
    def read_label_as_dict (self):

        """
        Function to load a ply file and the txt label file to the LabelledMesh object
        
        Args:
            path (str): String representing the path to the file.
            id (str): String representing the file id of the ply file.
            preprocessed (str): String representing the preprocessing step of the ply file.    
            label_name (str): name of the label file        
            exp_path (str): String representing the export folder where to save all derived data.                
        """        

        # path to the segmentation
        labelname = ''.join([self.path, self.id, self.label_name, ".txt"]) 

        # import label and create dictionary 
        df_label = pd.read_csv(labelname,skiprows=5,header=None,sep=' ',names=['a','b'],dtype=int)  # import txt segmentation 

        self.dict_label = dict(zip(df_label.a, df_label.b))

        self.unique_labels = get_unique_labels(self.dict_label)

    def extract_ridges (self):   

        """
        Function to get the ridges and centroids of the labelled areas on the surface of the labeledMesh object.
        The goal is extracting the outline vertices of each label.
        """

        # Create a dictionary of all vertices (keys), which have more than 1 neighbouring label and a list of all neighbouring vertices with the 
        # same label 
        
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
        # Calculate centroids of all labels        
        self.get_centroids()
        
    def get_centroids (self):
        # Create a dictionary of all vertices (keys), which have more than 1 neighbouring label and a list of all neighbouring vertices with the 
        # same label 
        self.centroids =    {label:np.mean([self.vertices[v] 
                                                for v in verts],axis=0)

                                for label, verts in self.label_outline_vertices.items()        
                            }

    def get_NNs (self):

        # Nearest neighbour (NN) from label centroid to submesh        
        self.NNs_to_mesh = {label: get_nearest_neighbor(self.tri_mesh,centroid)
                                
                                for label, centroid in self.centroids.items()
                            }

        self.get_label_submeshes()

        # Nearest neighbour (NN) from label centroid to submesh 
        self.NNs_to_submeshes = {label: get_nearest_neighbor(self.submeshes[label][0],centroid)
                                
                                    for label, centroid in self.centroids.items()
                                }    

    ## handelling of labelfile
    def get_label_submeshes (self):

        """
        Split mesh in submeshes according to imported labels.
        """        

        labels = get_uniquelabel_vertlist (self.dict_label)

        # Creates a dictionary of with a ridge point and the neighbours with the same label
        self.submeshes = create_label_submeshes (self.tri_mesh,labels)

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

        clust_verts = get_labels_IoU_max (self.dict_label,self.klabels) 

        clust_labels = {val:ul for ul,values in clust_verts.items() for val in values}

        write_labels_txt_file (clust_labels, ''.join ([ self.path, 
                                                        self.id,
                                                        '_'.join([  '',
                                                                    'Kmeans',
                                                                    'labels'])
                                                        ]))

    def kmeans_slice (self):
        """
        Slices mesh based on IoU_max of the k-means clustering and exports submeshes.

        """

        clust_verts = get_labels_IoU_max (self.dict_label,self.klabels) 

        clust_labels = {ul:{i:self.dict_label[n] for i,n in enumerate(values)} for ul,values in clust_verts.items()}

        submeshes = create_label_submeshes(self.tri_mesh,clust_verts)

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
                                                    '_labels']))

    def create_manual_edges(self):

        manual_Edges = manualEdges()
        manual_Edges.import_edges(self.path,self.id)

        self.manual_edges = manual_Edges.manual_edges

        

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

    ## nodes mesh
    def create_nodes_mesh (self,nodes,radius):

        nodes_list = [create_node_sphere (self.centroids [node],radius) for node in nodes]

        self.nodes_mesh = trimesh.util.concatenate(nodes_list)

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
                        label_name: str, 
                        exp_path: str = ''):
    
        """
        Function to prepare a polygraph from labbeled mesh.
        
        Args:
            path (str): String representing the path to the file.
            id (str): String representing the file id of the ply file.
            preprocessed (str): String representing the preprocessing step of the ply file.    
            label_name (str): name of the label file        
            exp_path (str): String representing the export folder where to save all derived data.                
        """  

        self.load_labelled_mesh (path, id, preprocessed, label_name, exp_path)

        self.extract_ridges()

        self.get_NNs()

    # preprocessing 
    def prep_ridges(self):


        self.ridge_neighbour_notshared_label = {key: {self.dict_label[v] for v in self.vertex_neighbors_dict[key] + [self.dict_label[key]] 
                                                if self.dict_label[key] != self.dict_label[v]}
                                                
                                        
                                        for key, v in enumerate(self.vertices) 
                                                if len(np.unique([self.dict_label[v] 
                                                    for v in self.vertex_neighbors_dict[key]] + [self.dict_label[key]])) > 1
                                            }                                                

        # Create a dictionary of all labels (keys) and a set of vertices with the same label (values), which belong to the ridge_neighbour_shared_label dictionary

        self.neighbouring_labels =   {ul: {self.dict_label[r_vert]
                                                for r_vert,labels in self.ridge_neighbour_notshared_label.items()
                                                for label in labels
                                                if self.dict_label[r_vert] != label and 
                                                ul == label
                                            }

                                        for ul in self.unique_labels
                                    }
    
        
        self.neighbouring_labels_set =   {(label,n_l)
                                            for label,neigh_labels in self.neighbouring_labels.items()
                                                for n_l in neigh_labels
                                        }       
              
    def polyline_to_nx (self):

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

    def get_connected_components (self):
        
        connected_components = nx.connected_components(self.graph_polyline)

        self.ccs = [list(cc)
                        for cc in connected_components]

    # preparing data for creating a pline 

    ## collecting the data necessary to create the header 
    def create_dict_mesh_info(self):

        self.dict_mesh_info =   {
                                'Mesh' :    self.id,
                                'Vertices': len(self.pline_vertices.keys()),
                                'Faces' :   len(self.faces),
                                'Polylines':len(self.polylines)
                                }
    
    ## collecting coordinates and normals of polyline vertices data necessary 
    def create_normals_vertices (self):
        
        self.pline_vertices = {}
        self.pline_normals = {}

        for polyline in self.polylines.values():    
            
            for n,vertex in enumerate(polyline):
                self.pline_vertices[n] = self.vertices[vertex]
                self.pline_normals[n] = self.normals[vertex]
                 
    def prepare_polyline (self):

        self.dict_plines = {n:{   
                                'label_id':self.polygraphs[n].nodes[polyline[0]]['label'],
                                'vertices':  polyline,
                                'vertices_no':  len(polyline),
                                }
                                    for n,polyline in self.polylines.items()
                                }     

    def export_pline(self):

        """       
        Export of Pline as pline file according to the GigaMesh Polyline Standard.
        """        

        exp_pline(self.path, self.id, self.dict_mesh_info, self.dict_plines, self.pline_vertices, self.pline_normals)

    def export_pline_funcvals(self,
                              funcvals,
                              var_name):
        """       
        Export of Pline function values as txt file according to the GigaMesh Polyline Standard.
        """        

        exp_pline_funcvals(self.path, self.id, self.dict_mesh_info, funcvals, var_name)

    # segmentate polyline 
    def polineline_segmenting(self):
      
        self.segments = { 
                    (label,n_l):    
                        {'vertices':[ v
                                        for v in self.dict_plines[label]['vertices'] 
                                            if n_l in self.ridge_neighbour_notshared_label[v]]}

                    for label,neigh_labels in self.neighbouring_labels.items()
                    for n_l in neigh_labels
                    if n_l in self.neighbouring_labels[label]
                }     

    def segment_pline_parameter (self,parameter):

        self.polineline_segmenting () 

        self.segments_funv = { 
                    (label,n_l):    
                        {'funct_vals':[ parameter[v]
                                        for v in self.dict_plines[label]['vertices'] if n_l in self.ridge_neighbour_notshared_label[v]]}

                    for label,neigh_labels in self.neighbouring_labels.items()
                    for n_l in neigh_labels
                    if n_l in self.neighbouring_labels[label]
                }

    def segment_to_ridgegraph(self):

        self.G_ridges = nx.Graph()    

        for edge,nodes in self.segments.items():
            if nodes != {'vertices': []}:

                self.G_ridges.add_nodes_from(edge)
                self.G_ridges.add_edge(*edge,
                                                nodes = nodes['vertices'],
                                                length = len(nodes['vertices']))
            else:
                continue

    def get_directed_edges(self,ridge_pairs):

        directed_edges = dict( [(r1,values['difference'] )
                                        for r1,values in ridge_pairs.items() 
                                            if values['bigger_smaller'] == -1.0] + 
                                    [(values['paired_scar'],values['difference'])  
                                        for values in ridge_pairs.values()
                                            if values['bigger_smaller'] == 1.0])
        # directed_edges = {( r1 if values['bigger_smaller'] == -1.0 else values['paired_scar']):values['difference'] 
        #                         for r1,values in ridge_pairs.items()}
        return directed_edges

    def create_direct_ridgegraph(self,ridge_pairs):

        directed_edges = self.get_directed_edges(ridge_pairs)
        
        directed_ridges = nx.DiGraph()

        for edge,difference in directed_edges.items():
            directed_ridges.add_nodes_from(edge)
            directed_ridges.add_edge(*edge,weight = difference)

        return directed_ridges

    def label_connections_nodes (self):

        label_vertices( self,
                        0,
                        self.connections_mesh.vertices,
                        # [''.join([f"{edges[0]:02}",'0',f"{edges[1]:02}"]) for edges in self.G_ridges.edges],
                        [num for num,_ in enumerate(self.G_ridges.edges, 1)], 
                        '_connections')

        label_vertices( self, 
                        len(self.connections_mesh.vertices),
                        self.nodes_mesh.vertices,
                        [num for num,_ in enumerate(self.G_ridges.nodes, 1)],
                        '_nodes')

    def direct_ridgegraph(self):

        self.DiG_ridges = {}

        self.DiG_ridges ['normal'] = self.create_direct_ridgegraph(self.ridges_pairs) 

        self.DiG_ridges ['max']  = self.create_direct_ridgegraph(self.ridges_pairs_max) 

        self.DiG_ridges ['min']  = self.create_direct_ridgegraph(self.ridges_pairs_min) 
   
    def get_DiG_ridge_properties(self,graphname):       

        self.DiG_properties = get_basic_graph_properties(self.DiG_ridges [graphname])

    def get_G_ridge_properties(self):

        self.G_properties = get_basic_graph_properties(self.G_ridges)

    def export_DiG_node_properties(self):

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

        G_node_degree = {key:self.G_properties[val]['degree'] 
                         for key,val in self.dict_label.items() if val not in self.no_polyline}

        G_node_degree_weighted = {key:self.G_properties[val]['degree_weigthed'] 
                                  for key,val in self.dict_label.items() if val not in self.no_polyline}

        G_node_betweenness = {key:self.G_properties[val]['betweenness_centrality'] 
                              for key,val in self.dict_label.items() if val not in self.no_polyline}

        write_labels_txt_file (G_node_degree, ''.join([self.path, self.id, '_G-node_degree',str(self.nrad)])) 

        write_labels_txt_file (G_node_degree_weighted, ''.join([self.path, self.id, '_G-node_degree_weighted',str(self.nrad)]))    
        
        write_labels_txt_file (G_node_betweenness,''.join([self.path, self.id, '_G-node_betweenness',str(self.nrad)]))  

