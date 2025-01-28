"""
========================
MSII Classes 
========================
"""

from util import *

# import numpy as np

import networkx as nx
from scipy.spatial import distance


from DetermineRidges.RidgeAnalysis import PolylineGraphs
from Classes.BasicClasses import Pline,manualEdges,NpEncoder

from Functions.EssentialGraphFunctions import get_basic_graph_properties

# data export 
import json

# Decorator to time Functions
from Functions.EssentialDecorators import timing

# from IntegralInvariants.II1DFunctions import create_start_list,get_longest_outline,create_icospheres,get_all_crossingpoints

# writing txt files
from Functions.exportFiles.writeTxt import write_labels_txt_file,write_funvals_txt_file,write_feature_vectors_txt_file

from Functions.PolylineGraph import create_start_list,create_polyline,line_sphere_intersection,get_cycle,get_longest_outline #,get_max_outline,get_connected_components,
from Functions.BasicMSII1D import test_nodes_two_neigh,angle_between_vectors

# Functions  for creating 3D shaped connections of graph models
# from Classes.Primitive_3D.EdgeShapes3D import generate_unitarrow,generate_unitconnection
from Functions.Essential3DPlotting import arrow_trafomat,create_rotated_arrow,connection_trafomat,create_rotated_connection

# import IntegralInvariants.integralInvariant1D as II1D
# alpha version 0.0.1

class MSIIPline(PolylineGraphs):

    """
    The MSIIPline object is a child object of the Pline and LabelledMesh objects.
    """

    def __init__(   self,
                    path: str = None,
                    id: str = None,
                    preprocessed: str = None,                
                    dict_mesh_info: dict = None,
                    dict_plines: dict = None,
                    vertices: np.ndarray = None,
                    normals: np.ndarray = None):
        
        """
        MSIIPline

        Attributes:
            path (str): String representing the path to the file.
            id (str): String representing the file id of the ply file.
            preprocessed (str): String representing the preprocessing stage of the ply file.
            dict_mesh_info (dict): Any metadata about the mesh.
            dict_plines (dict): Any data of the polylines.
            vertices (ndarray): Array of vertex locations with shape (n, 3).
            normals (ndarray): Array of normal vectors for vertices with shape (n, 3).
        
        """

        super().__init__()

        # check for None only to avoid warning messages in subclasses
        if path is not None:
            self.path = path
        if id is not None:
            self.id = id
        if preprocessed is not None:
            self.preprocessed = preprocessed
        if dict_mesh_info is not None:
            self.dict_mesh_info = dict_mesh_info
        if dict_plines is not None:
            self.dict_plines = dict_plines
        if vertices is not None:
            self.vertices = vertices            
        if normals is not None:
            self.normals = normals                      

    def create_from_mesh(self,
                         path,
                         id,
                         dict_mesh_info,
                         dict_plines,
                         vertices,
                         normals):
        
        """
        Import values referencing to the labelled mesh.

        Attributes:
            path (str): String representing the path to the file.
            id (str): String representing the file id of the ply file.
            preprocessed (str): String representing the preprocessing stage of the ply file.
            dict_mesh_info (dict): Any metadata about the mesh.
            dict_plines (dict): Any data of the polylines.
            vertices (ndarray): Array of vertex locations with shape (n, 3).
            normals (ndarray): Array of normal vectors for vertices with shape (n, 3).        
        """

        self.path = path 
        self.id = id
        self.filename = ''.join([self.path, self.id,'_polyline.pline'])        

        self.dict_mesh_info = dict_mesh_info
        self.dict_plines = dict_plines
        self.vertices = vertices
        self.normals = normals

    def create_from_Pline (self,pline):

        self.create_from_mesh(pline.path, pline.id,pline.dict_mesh_info,pline.dict_plines,pline.vertices,pline.normals)


    def polygraphs_to_graph (self):

        self.polygraphs = {}

        for ind,values in self.dict_plines.items():

            G = create_polyline (values['vertices'])

            self.polygraphs[ind] = {'G':G, 'label_id':values['label_id']}

        # self.polygraphs = polygraphs

    @timing
    def calc_II_new_sphere (self,maxrad,nradii):

        self.maxrad = maxrad
        self.nrad = nradii

        self.polylinedata = {}

        start = maxrad / self.nrad 

        self.radii = np.linspace(start, maxrad, self.nrad)

        self.iterate_polygraphs_new_sphere()

    @timing
    def iterate_polygraphs_new_sphere (self):

        for label,G in self.polygraphs.items():

            self.label = int(label)
            self.polylinedata[self.label] = {}

            self.G = G['G']

            self.len_nodes = len(self.G.nodes())    

            self.get_intersects_new()

    @timing
    def get_intersects_new (self):
        
        intersects = {}
        polyline,rev_polyline = get_cycle(self.G)

        for node in polyline:
        
            intersects [node] = {}  

            temp_polyline = create_start_list(polyline,polyline.index(node))    

            rev_temp_polyline =  create_start_list(rev_polyline,rev_polyline.index(node))      

            intersects [node] = {float(radius):self.find_intersects_new(self.vertices,temp_polyline,rev_temp_polyline,radius) for radius in self.radii}       #(self,vertices,poly,rev_poly,treshold)

            self.polylinedata[self.label] = intersects

    def try_complete_graph_intersect_new(self,G,vertices,node,polyline,radius):

        intersects = self.find_intersects_new(self.vertices,polyline,radius) 

        try: 
            if not len(intersects['down_stream'] ['II1D_crsp']) > 0 or not len(intersects ['up_stream']['II1D_crsp']) > 0 :

                neighs = list(nx.neighbors(G,node))

                polyline = get_longest_outline(G,node,neighs[0])

                intersects = self.find_intersects_new(vertices,polyline,radius) 

            else: 
                intersects = intersects
        except:
            intersects = {'down_stream':{'II1D_crsp':np.array([0,0,0])}}
            intersects.update({'up_stream':{'II1D_crsp':np.array([0,0,0])}})

        return intersects

    def find_intersects_new(self,vertices,poly,rev_poly,treshold):   
                
        down_stream = self.stream_intersect_new(vertices,rev_poly,treshold)
        up_stream = self.stream_intersect_new(vertices,poly,treshold)

        dist_pnts = {
                    'down_stream':down_stream,
                    'up_stream':up_stream
                    }
        
        return dist_pnts

    #intersection functions
    def stream_intersect_new(self,vertices,pol,treshold):

        dist_pnts_dict = {'euclidean_dist':{},
                        'dist':{},
                        'first_node_outside':{},
                        'II1D_crsp':{},
                        'node_dist':{}}

        dist = 0
        n_pos = 0
                    
        for pos in range(len(pol)-1):

            n_pos += 1
            euclid_dist = distance.euclidean(vertices[pol[0]],vertices[pol[n_pos]]) 
            
            
            if euclid_dist > treshold:                    

                II1D_crsp = line_sphere_intersection(vertices[pol[pos]],vertices[pol[n_pos]], vertices[pol[0]], treshold)                

                dist += distance.euclidean( vertices[pol[pos]],
                                            II1D_crsp)

                dist_pnts_dict ['euclidean_dist'] = euclid_dist
                dist_pnts_dict ['II1D_crsp'] = II1D_crsp
                dist_pnts_dict ['dist'] = dist         
                dist_pnts_dict ['first_node_outside'] = pol[n_pos] 
                dist_pnts_dict ['node_dist'] = pos 

                return dist_pnts_dict
                            
            else:
                dist += distance.euclidean( vertices[pol[pos]],vertices[pol[n_pos]])    

        dist_pnts_dict ['euclidean_dist'] = euclid_dist
        dist_pnts_dict ['II1D_crsp'] = 0
        dist_pnts_dict ['dist'] = dist         
        dist_pnts_dict ['first_node_outside'] = None 
        dist_pnts_dict ['node_dist'] = len(pol) 

        return dist_pnts_dict 

    # import polylinedata from json file
    @timing
    def json_import_polylinedata(self):

        with open('MSII_polylinedata.json','r') as f:
            self.polylinedata = json.loads(json.load(f))

    # save polyline as json
    def MSII_polylinedata_to_json(self):

        json_dump = json.dumps( self.polylinedata, 
                                cls=NpEncoder)
        with open('{0}{1}{2}_MSII_polylinedata.json'.format(self.path,self.id), 'w') as fp:
            json.dump(json_dump, fp)

    # extract from polylinedata
    @timing        
    def polylinedata_angle(self):
        self.list_angle = []
        list_angle = []
        self.dict_angle = {}    
        for values in self.polylinedata.values():
            for node, vals in values.items():        
                self.dict_angle[node] = {}
                for rad,v in vals.items():
                    self.dict_angle[node][rad] = {}

                    try:
                        angle = angle_between_vectors(   list(v['down_stream']['II1D_crsp']),
                                                    self.vertices[node],
                                                    list(v['up_stream']['II1D_crsp']))
                        self.dict_angle[node][rad] = {'angle': angle}
                        list_angle.append([node,rad,angle[0]])
                        self.list_angle.append(['{} {} {}'.format(node,rad,angle[0])])
                        
                    except:
                        self.dict_angle[node][rad] = { 'angle': (0,0)} 
                        list_angle.append([node,rad,0])    
                        self.list_angle.append(['{} {} {}'.format(node,rad,0)])
    
    @timing    
    def polylinedata_dist(self):
        self.list_dist = []
        list_dist = []
        self.dict_dist = {}
        for values in self.polylinedata.values():
            for node, vals in values.items():        
                self.dict_dist[node] = {}
                for rad,v in vals.items():
                    self.dict_dist[node][rad] = {}
                    try:
                        dist_total = v['down_stream']['dist'] + v['up_stream']['dist']
                        self.dict_dist[node][rad] = {'dist_total':dist_total}
                        list_dist.append([node,rad,dist_total])
                        self.list_dist.append(['{} {} {}'.format(node,rad,dist_total)])                    

                    except:
                        self.dict_dist[node][rad] = {'dist_total': 0}   
                        list_dist.append([node,rad,0])                      
                        self.list_dist.append(['{} {} {}'.format(node,rad,0)])       

        self.array_dist = np.array(list_dist)  

    ## extract polylinedata_angle and polylinedata_dist
    def get_feature_vectors (self): 

        self.polylinedata_dist()

        self.polylinedata_angle()

        self.angle_feature_vector = {node:[list(angle['angle'])[0] for angle in  II.values()] for node, II in self.dict_angle.items()}
        write_feature_vectors_txt_file (self.angle_feature_vector,
                                        ''.join([self.path, self.id]),
                                        '_ang-vec-n{:02d}-r{:.2f}.txt'.format(self.nrad,self.maxrad)) 
                                        
        
        self.max_angle = {node: max(angle_list, key=abs) for node, angle_list in self.angle_feature_vector.items()}
        write_funvals_txt_file (self.max_angle,
                                ''.join([self.path, self.id]),
                                '_max-ang-vec-n{:02d}-r{:.2f}.txt'.format(self.nrad,self.maxrad)) 

        self.distance_feature_vector = {node:[dist['dist_total'] for dist in II.values()] for node, II in self.dict_dist.items()}
        write_feature_vectors_txt_file (self.distance_feature_vector,
                                        ''.join([self.path, self.id]),
                                        '_dst-vec-n{:02d}-r{:.2f}.txt'.format(self.nrad,self.maxrad)) 

        
    # generate dictioaries for exporting angle as function values
    @timing    
    def select_radius_angle (self,radius):
        
        self.dict_radius_selected_angle = { vertex: list(vals['angle'])[0] 
                                                
                                            for vertex, values in self.dict_angle.items() 
                                                    
                                                    for rad, vals in values.items() 
                                                        
                                                    if rad == radius}
    
    @timing
    def get_all_radii_angle (self):

        self.dict_radii_all_angle = {   rad:

                                            {vertex:[vals['angle'][0] for vals in values.values()] 
                                            for vertex,values in self.dict_angle.items() } 

                                        for vertex,values in self.dict_angle.items() for rad in values.keys() }

    # generate dictioaries for exporting distance as function values   
    @timing  
    def select_radius_dist (self,radius):
        
        self.dict_radius_selected_dist = {  vertex:vals['dist_total'] 

                                            for vertex, values in self.dict_dist.items() 

                                                for rad, vals in values.items() 

                                                if rad == radius}
    
    @timing
    def get_all_radii_dist (self):

        self.dict_radii_all_dist = { rad:

                                        {vertex:[vals['dist_total'] for vals in values.values()] 
                                            for vertex,values in self.dict_dist.items() } 

                                    for values in self.dict_angle.values() for rad in values.keys() }

class MSIIGraphs(MSIIPline): 

    def __init__(self):
        super().__init__()

    @timing
    def segment_to_graph_MSII(self):

        self.G_ridges = nx.Graph()

        self.mean_segments_funv_node = {}

        self.mean_segments_funv = {}        
        self.mean_maxsegments_funv = {}
        self.mean_minsegments_funv = {}                

        for edge,nodes in self.segments.items():
            if nodes != {'vertices': []}:

                self.G_ridges.add_nodes_from(edge)
                self.G_ridges.add_edge(*edge,
                                        nodes = nodes['vertices'],
                                        length = len(nodes['vertices']),
                                        
                                        funct_vals = self.segments_funv[edge]['funct_vals'],
                                        max = np.round(np.max(self.segments_funv[edge]['funct_vals'])),
                                        mean = np.mean(self.segments_funv[edge]['funct_vals']),
                                        med = np.median(self.segments_funv[edge]['funct_vals']),
                                        std = np.std(self.segments_funv[edge]['funct_vals']),
                                        var = np.var(self.segments_funv[edge]['funct_vals']))
        
                for node in nodes['vertices']:
                    
                    self.mean_segments_funv_node [node] = {}
                    
                    self.mean_segments_funv_node [node] = np.mean(self.segments_funv[edge]['funct_vals'])
    

                self.mean_segments_funv[edge] = np.mean(self.segments_funv[edge]['funct_vals'])
                self.mean_maxsegments_funv[edge] = np.max(self.segments_funv[edge]['funct_vals'])
                self.mean_minsegments_funv[edge] = np.max(self.segments_funv[edge]['funct_vals'])

            else:
              

                self.mean_segments_funv[edge] = 0
                self.mean_maxsegments_funv[edge] = 0
                self.mean_minsegments_funv[edge] = 0

    @timing
    def ridge_pairs(self):

        """
        Calculates ridge pairs and their differences in mean, max, and min segment values.

        Attributes:
            ridges_pairs (dict): dictionary containing edges as tuples (keys) and nested dictionary derived from mean segment values with 3 keys:
                                    - 'paired_scar' :   reversed ordered edge (tuple)
                                    - 'bigger_smaller': sign of difference. 
                                    - 'difference':     difference between mean func values between vertices belonging to edge[0] and edge[1]. 
                                                        Note: Due to the adjacency of labels, segments consist of borders of two labels at once. 
                                                                                
            ridges_pairs_max (dict): Similar to `ridges_pairs` but for maximum segment values.
            ridges_pairs_min (dict): Similar to `ridges_pairs` but for minimum segment values.

        """        


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

    @timing
    def segment_pline_selected_radius(self,nrad):

        self.nrad = nrad
        
        self.polineline_segmenting () 

        self.segments_funv = { 
                    (label,n_l):    
                        {'funct_vals':[ self.angle_feature_vector[v][self.nrad]
                                        for v in self.dict_plines[label]['vertices'] if n_l in self.ridge_neighbour_notshared_label[v]]}

                    for label,neigh_labels in self.neighbouring_labels.items()
                    for n_l in neigh_labels
                    if n_l in self.neighbouring_labels[label]
                }

class MSIIChaineOperatoire (MSIIGraphs):

    def __init__(self):
        super().__init__()

    def create_chaine_operatoire (self,graphtype,radius_scale,circumference_scale):

        self.create_nodes_mesh(self.DiG_ridges[graphtype].nodes,radius_scale)

        self.create_arrows_mesh(self.DiG_ridges[graphtype],circumference_scale)

        self.create_ridges_mesh()

        self.ridges_arrows_mesh = trimesh.util.concatenate([self.arrows_mesh,self.nodes_mesh,self.ridges_mesh])        

        self.ridges_arrows_mesh.export(''.join ([self.path, 
                                                 self.id,
                                                 '-'.join(['_MSII','links',str(graphtype),'r{}'.format(str(self.radii[self.nrad]))]),                                       
                                                 '.ply']),
                                                 file_type='ply')

    # edge width scaled by edge weight 
    def create_rotated_scaled_arrow (self, edge, DiG):

        arrow_transformed = None

        origin, target = self.centroids [edge[0]], self.centroids [edge[1]]

        scale = distance.euclidean(origin, target)

        _, trafomat = angle_between_vectors(origin + [0,0,scale],
                                    origin,
                                    target)
        
        trafomat = np.vstack((trafomat.T,origin))

        trafomat = np.vstack((trafomat.T,np.array([0,0,0,0])))
        
        arrow_transformed = arrow_trafomat(DiG.edges[edge]['weight']/self.max_weight,scale, trafomat)

        return trafomat,arrow_transformed

    def create_arrows_mesh (self,DiG,circumference):
        
        # self.max_weight = 1

        arrow_list = [create_rotated_arrow (edge,self.centroids,circumference)[1] for edge in DiG.edges]

        self.arrows_mesh = trimesh.util.concatenate(arrow_list)

    def create_chaine_operatoire_labels (self):
        vert_dict = {n_vert:1 for n_vert in range(0,len(self.arrows_mesh.vertices))}
        vert_dict.update({len(vert_dict.keys()) + n_vert + 1:2 for n_vert in range(0,len(self.nodes_mesh.vertices))})
        vert_dict.update({len(vert_dict.keys()) + n_vert + 1:3 for n_vert in range(0,len(self.ridges_mesh.vertices))})
        self.vert_dict = vert_dict

    def create_chaine_operatoire_functvals (self,graphtype):

        num_arrow_verts = int(len(self.arrows_mesh.vertices)/len(self.DiG_ridges[graphtype].edges))

        self.arrow_dict_funcval = {}

        for n,edge in enumerate(self.DiG_ridges[graphtype].edges):
            for i in range (0 + n * num_arrow_verts, 99 + n * num_arrow_verts):

                self.arrow_dict_funcval [i] = self.DiG_ridges[graphtype].edges[edge]['weight']


        vert_dict = {n_vert:self.arrow_dict_funcval[n_vert] for n_vert in range(0,len(self.arrows_mesh.vertices))}
        vert_dict.update({len(vert_dict.keys()) + n_vert + 1:2 for n_vert in range(0,len(self.nodes_mesh.vertices))})
        vert_dict.update({len(vert_dict.keys()) + n_vert + 1:3 for n_vert in range(0,len(self.ridges_mesh.vertices))})
        self.vert_dict = vert_dict        

    # def label_connections_nodes (self):
    #     label_vertices(  self,
    #             0,
    #             self.connections_mesh.vertices,
    #             self.G_ridges.nodes, 
    #             '_connections')

    #     label_vertices(  self, 
    #             len(self.connections_mesh.vertices),
    #             self.nodes_mesh.vertices,
    #             self.centroids.keys(),
    #             '_nodes')
        
    def export_max_func_val (self,func_val_name):    



        write_funvals_txt_file (self.max_func_val,
                                ''.join([self.path, self.id]),
                                '_{}.txt'.format(func_val_name))

        # write_labels_txt_file ( self.max_func_val, 
        #                         ''.join ([  self.path, 
        #                                     self.id,
        #                                     '_'.join([  '',
        #                                                 func_val_name,
        #                                                 'labels'])
        #                                 ])
        #                         )  

    def export_chaine_operatoire_labels (self,label_dict):

        write_labels_txt_file (label_dict,''.join([self.path, self.id, '_label'])) 

    def export_chaine_operatoire_functvals (self,label_dict):

        write_labels_txt_file (label_dict,''.join([self.path, self.id, str(self.nrad), '_functval']))  

