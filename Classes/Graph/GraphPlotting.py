"""
========================
ChaineOperatoire Classes 
========================
"""

from util import *

# import numpy as np

import networkx as nx
from scipy.spatial import distance


from DetermineRidges.RidgeAnalysis import PolylineGraphs
from Classes.BasicClasses import Pline,manualEdges,NpEncoder

from Functions.EssentialGraphFunctions import get_basic_graph_properties

from Functions.BasicMSII1D import angle_between_vectors

# data export 
import json

# Decorator to time Functions
from Functions.EssentialDecorators import timing

# writing txt files
from Functions.exportFiles.writeTxt import write_labels_txt_file

# Functions  for creating 3D shaped connections of graph models
# from Classes.Primitive_3D.EdgeShapes3D import generate_unitarrow,generate_unitconnection
from Functions.Essential3DPlotting import arrow_trafomat,create_rotated_arrow,connection_trafomat,create_rotated_connection,create_labeling_arrows


class ChaineOperatoire (PolylineGraphs):

    def __init__(self):
        super().__init__()

    def edges_to_ridgegraph(self):

        self.G_ridges = nx.Graph()

        for edge in self.manual_edges:
            self.G_ridges.add_nodes_from(edge)
            self.G_ridges.add_edge(*edge)

    def direct_ridgegraph(self):

        self.DiG_manual = nx.DiGraph()

        for edge in self.manual_edges:
            self.DiG_manual.add_nodes_from(edge)
            self.DiG_manual.add_edge(*edge)

    def create_direct_ridgegraph(directed_edges):
        
        directed_ridges = nx.DiGraph()

        for edge,weight in directed_edges.items():
            directed_ridges.add_nodes_from(edge)
            directed_ridges.add_edge(*edge,weight = weight)

        return directed_ridges            

    def create_chaine_operatoire (  self,
                                    circumference,
                                    radius):

        self.create_arrows_mesh(self.DiG_manual,
                                circumference)

        self.create_nodes_mesh( self.centroids,
                                radius)

        self.create_ridges_mesh()

        self.ridges_arrows = trimesh.util.concatenate([ self.arrows_mesh,
                                                        self.nodes_mesh,
                                                        self.ridges_mesh])        
        

        self.ridges_arrows.export(''.join ([self.path, 
                                            self.id,
                                            self.edge_name,
                                            '_ridges-arrows', 
                                            '.ply']),
                                            file_type='ply')       

  
    def create_arrows_mesh (self, 
                            DiG,
                            circumference):

        self.arrows_list = [create_rotated_arrow (edge,self.centroids,circumference)[1] for edge in DiG.edges]

        self.arrows_mesh = trimesh.util.concatenate(self.arrows_list)

    def create_chaine_operatoire_labels (self):
        vert_dict = {n_vert:1 for n_vert in range(0,len(self.arrows_mesh.vertices))}
        vert_dict.update({len(vert_dict.keys()) + n_vert + 1:2 for n_vert in range(0,len(self.nodes_mesh.vertices))})
        vert_dict.update({len(vert_dict.keys()) + n_vert + 1:3 for n_vert in range(0,len(self.ridges_mesh.vertices))})
        self.vert_dict = vert_dict

    def create_chaine_operatoire_functvals (self,manu_type):

        num_arrow_verts = int(len(self.arrows_mesh.vertices)/len(self.DiG_manual.edges))

        mE = manualEdges()
        if manu_type == 'edges':
            mE.import_edges(self.path, self.id )
            
        elif manu_type == 'edges_nodes':
            mE.import_edges_nodes(self.path, self.id )

        else:
            print('no reference for edges provided')
            return          

        edges = mE.manual_edges

        correct_edges,_ = evaluate_directed_edges(edges,self.manual_edges)

        self.arrow_dict_funcval = {}

        for n,edge in enumerate(self.DiG_manual.edges):
            for i in range (0 + n * num_arrow_verts, 99 + n * num_arrow_verts):
                if edge in correct_edges.keys():
                    self.arrow_dict_funcval [i] = 2  
                elif edge not in correct_edges.keys():                
                    self.arrow_dict_funcval [i] = 1 

                # self.arrow_dict_funcval [i] = correct_edges[edge]


        vert_dict = {n_vert:self.arrow_dict_funcval[n_vert] for n_vert in range(0,len(self.arrows_mesh.vertices))}
        vert_dict.update({len(vert_dict.keys()) + n_vert + 1:2 for n_vert in range(0,len(self.nodes_mesh.vertices))})
        vert_dict.update({len(vert_dict.keys()) + n_vert + 1:3 for n_vert in range(0,len(self.ridges_mesh.vertices))})
        self.vert_dict = vert_dict        

    def export_chaine_operatoire_labels (self,label_dict):

        print(''.join([ self.path, 
                                                    self.id, 
                                                    self.edge_name,
                                                    '_label']))

        write_labels_txt_file (label_dict,''.join([ self.path, 
                                                    self.id, 
                                                    self.edge_name,
                                                    '_label'])) 

    def export_chaine_operatoire_functvals (self,label_dict):

        write_labels_txt_file (label_dict,''.join([ self.path, 
                                                        self.id, 
                                                        self.edge_name,
                                                        '_functval']))          
  
    def segment_pline_manual(self):
       
        self.segments = { 
                    (label,n_l):    
                        {'vertices':[ v
                                        for v in self.dict_plines[label]['vertices'] if n_l in self.dict_ridge_notshared_label[v]]}

                    for label,neigh_labels in self.neighbouring_labels.items()
                    for n_l in neigh_labels
                    if n_l in self.neighbouring_labels[label]
                }
        
    def export_DiG_gexf (self):

        nx.write_gexf(self.DiG_manual, ''.join([self.path, 
                                                self.id,
                                                'edge_name',
                                                '_ridges_arrows',
                                                '.gexf']))
        
    # creating and exporting labels for 3D plotting for the 3D representation of the ChaineOperatoire 
    def create_3D_label(self):
        """
        Create and export 3D labels for the object's meshes.

        This function creates a dictionary of vertex labels for arrows, nodes, and
        ridges meshes. It then updates this dictionary with labels for nodes and ridges
        before exporting the labels using `export_arrow_labels`.

        Args:
            self (object): Current ChaineOperatoire object instance.
        """
        vert_dict = {n + n_arr * len(arrow.vertices): label 
                        for n_arr,arrow in enumerate(self.arrows_list) 
                            for n,label in enumerate(create_labeling_arrows(arrow))}

        vert_dict.update({len(vert_dict.keys()) + n_vert + 1: 0 
                            for n_vert in range(0,len(self.nodes_mesh.vertices))})
        vert_dict.update({len(vert_dict.keys()) + n_vert + 1: 4 
                            for n_vert in range(0,len(self.ridges_mesh.vertices))})

        self.export_arrow_labels(vert_dict)

    def export_arrow_labels(self,
                            labels_dict: dict):
        
        """
        Export the arrow labels to a text file.
        
            self (object): Current ChaineOperatoire object instance.
            labels_dict (dict): A dictionary containing the labels.
        """
        print(''.join([self.path, 
                                                    self.id, 
                                                    self.preprocessed,
                                                    self.edge_name,
                                                    '-label']))

        write_labels_txt_file (labels_dict,''.join([self.path, 
                                                    self.id, 
                                                    self.preprocessed,
                                                    self.edge_name,
                                                    '-label'])) 

class GraphEvaluation (PolylineGraphs):

    def __init__(self):
        super().__init__()

    def manual_operational_sequences_edges (self):

        edge_df = pd.read_csv(''.join([self.path,self.id,'_links','.csv']),
                                sep=',',header=0)

        self.manual_edges  = {(int(edge[0]),int(edge[1])) for _,edge in edge_df.iterrows()}

    def manual_operational_sequences_nodes_edges (self):

        nodes_df = pd.read_csv(''.join([self.path,self.id,'_nodes','.csv']),
                                sep=',',header=0)

        self.manual_nodes = {node[-1]: {nodes_df.columns[n]:para for n,para in enumerate(node[:-1])} 
                    
                        for _,node in nodes_df.iterrows()
                        }
        
        edge_df = pd.read_csv(''.join([self.path,self.id,'_links','.csv']),
                                sep=',',header=0)

        
        self.manual_edges = {(int(nodes_df[nodes_df['node'] == edge['source']]['gt_label']),
                        int(nodes_df[nodes_df['node'] == edge['target']]['gt_label']))
                    
                        for _,edge in edge_df.iterrows()}


            
    def create_undirected_model (self,radius_scale,circumference):

        self.create_connections_mesh(self.centroids,self.G_ridges.edges,circumference)

        self.create_nodes_mesh(self.centroids,radius_scale) # ,circumference_scale

        self.create_ridges_mesh()

        self.ridges_connections_mesh = trimesh.util.concatenate([   self.connections_mesh,
                                                                    self.nodes_mesh,
                                                                    self.ridges_mesh])        

        self.ridges_connections_mesh.export(''.join ([self.path, 
                                            self.id,
                                            '_ridge_connections', 
                                            '.ply']),
                                            file_type='ply')
    
    # edge width scaled by edge weight 
    def create_rotated_scaled_connection (self, locations,edge):

        connection_transformed = None

        origin, target = self.centroids [edge[0]], self.centroids [edge[1]]

        scale = distance.euclidean(origin, target)

        _, trafomat = angle_between_vectors(origin + [0,0,scale],
                                    origin,
                                    target)
        
        trafomat = np.vstack((trafomat.T,origin))

        trafomat = np.vstack((trafomat.T,np.array([0,0,0,0])))
        
        return trafomat,connection_transformed

    def create_connections_mesh (self,locations,edges,scales):
        
        # self.max_weight = 1

        connections_list = [create_rotated_connection (edge,locations,scales)[1] for edge in edges]

        self.connections_mesh = trimesh.util.concatenate(connections_list)

    def create_graph_model_simple_labels (self):
        
        vert_dict = {n_vert:1 for n_vert in range(0,len(self.connections_mesh.vertices))}
        vert_dict.update({len(vert_dict.keys()) + n_vert + 1:0 for n_vert in range(0,len(self.nodes_mesh.vertices))})
        vert_dict.update({len(vert_dict.keys()) + n_vert + 1:0 for n_vert in range(0,len(self.ridges_mesh.vertices))})
        self.vert_dict = vert_dict

    def create_graph_model_selected_labels (self,edge_label):

        num_graph_model_verts = int(len(self.connections_mesh.vertices)/len(self.G_ridges.edges))
        self.connection_label = {}

        for n,edge in enumerate(self.G_ridges.edges):
            for i in range (0 + n * num_graph_model_verts, 99 + n * num_graph_model_verts):
                if edge in edge_label.keys():
                    self.connection_label [i] = 2  
                elif edge not in edge_label.keys():                
                    self.connection_label [i] = 1 
                        
        
        vert_dict = {n_vert:self.connection_label[n_vert] for n_vert in range(0,len(self.connections_mesh.vertices))}
        vert_dict.update({len(vert_dict.keys()) + n_vert + 1:0 for n_vert in range(0,len(self.nodes_mesh.vertices))})
        vert_dict.update({len(vert_dict.keys()) + n_vert + 1:0 for n_vert in range(0,len(self.ridges_mesh.vertices))})
        self.vert_dict = vert_dict


    def create_graph_model_functvals (self):

        num_graph_model_verts = int(len(self.connections_mesh.vertices)/len(self.G_ridges.edges))

        self.connection_dict_funcval = {}

        for n,edge in enumerate(self.G_ridges.edges):
            for i in range (0 + n * num_graph_model_verts, 99 + n * num_graph_model_verts):

                self.connection_dict_funcval [i] = self.G_ridges.edges[edge]['weight']


        vert_dict = {n_vert:self.connection_dict_funcval[n_vert] for n_vert in range(0,len(self.connections_mesh.vertices))}
        vert_dict.update({len(vert_dict.keys()) + n_vert + 1:0 for n_vert in range(0,len(self.nodes_mesh.vertices))})
        vert_dict.update({len(vert_dict.keys()) + n_vert + 1:0 for n_vert in range(0,len(self.ridges_mesh.vertices))})
        self.vert_dict = vert_dict        

    def export_graph_model_labels (self,label_dict,para_name):

        write_labels_txt_file (label_dict,''.join([self.path, self.id, '_', para_name, '-label'])) 

    def export_graph_model_functvals (self,label_dict):

        write_labels_txt_file (label_dict,''.join([self.path, self.id, '_', str(self.nrad), '-functval']))         
  
    def segment_pline_manual(self):
       
        self.segments = { 
                    (label,n_l):    
                        {'vertices':[ v
                                        for v in self.dict_plines[label]['vertices'] if n_l in self.ridge_neighbour_notshared_label[v]]}

                    for label,neigh_labels in self.neighbouring_labels.items()
                    for n_l in neigh_labels
                    if n_l in self.neighbouring_labels[label]
                }
