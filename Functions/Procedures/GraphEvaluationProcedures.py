import os,sys

currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from util import *

# compare two operational sequences 
from Functions.EvaluateGraph import directededges_parameters, export_links

from Functions.EssentialEdgesFunctions import get_manual_edges

def undirected_graph_procedure (obj,**kwargs):

    # LabelledMesh init
    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelname = kwargs ['labelname']
    exp_path = kwargs ['exp_path'] 

    # Data import 
    obj.load_labelled_mesh(path,id,preprocessed,labelname,exp_path) 
    obj.extract_ridges()

    # get polylines
    obj.edges_to_polygraphs()
    obj.polygraphs_to_polylines()

    # create node coordinates
    obj.get_centroids()
    # obj.get_NNs()
    # obj.get_NNs()

    # prepare for creating MSII1D_Pline object 
    obj.create_normals_vertices()
    obj.create_dict_mesh_info()
    obj.prepare_polyline()

    # prepare for get ridges and for scar-ridge-graph model and leading to chaine-operatoire 
    obj.prep_ridges()
    obj.polineline_segmenting()
    obj.segment_to_graph()


def graph_evaluation_procedure (obj,**kwargs):

    # LabelledMesh init
    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelname = kwargs ['labelname']
    exp_path = kwargs ['exp_path'] 

    # scales
    radius_scale = kwargs ['radius_scale'] 
    circumference_scale = kwargs ['circumference_scale'] 

    # Data import 
    obj.load_labelled_mesh(path,id,preprocessed,labelname,exp_path) 
    obj.extract_ridges()

    # get polylines
    obj.edges_to_polygraphs()
    obj.polygraphs_to_polylines()

    # create node coordinates
    obj.get_centroids()
    # obj.get_NNs()
    # obj.get_NNs()

    # prepare for creating MSII1D_Pline object 
    obj.create_normals_vertices()
    obj.create_dict_mesh_info()
    obj.prepare_polyline()

    # prepare for get ridges and for scar-ridge-graph model and leading to chaine-operatoire 
    obj.prep_ridges()
    obj.polineline_segmenting()
    obj.segment_to_graph()

    obj.create_undirected_model(radius_scale,circumference_scale)

# @timing
def graph_direct_parameter_procedure (obj,**kwargs):

    # LabelledMesh init
    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelname = kwargs ['labelname']
    exp_path = kwargs ['exp_path'] 

    # Data import 
    obj.load_labelled_mesh(path,id,preprocessed,labelname,exp_path) 
    obj.extract_ridges()

    # get polylines
    obj.edges_to_polygraphs()
    obj.polygraphs_to_polylines()

    # create node coordinates
    obj.get_centroids()
    # obj.get_NNs()
    # obj.get_NNs()

    # prepare for creating MSII1D_Pline object 
    obj.create_normals_vertices()
    obj.create_dict_mesh_info()
    obj.prepare_polyline()

    # prepare for get ridges and for scar-ridge-graph model and leading to chaine-operatoire 
    obj.prep_ridges()
    obj.polineline_segmenting()
    obj.segment_to_graph()

    obj.G_network_parameters = {
                            'degree': nx.degree(obj.G_ridges),
                            'betweenness': nx.betweenness_centrality(obj.G_ridges)
                            }
    
    edges = get_manual_edges(path, id)

    for k,v in obj.G_network_parameters.items():

        directededges_parameters(path,id,edges,v,k)


# @timing
def direct_graph_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    para_name = kwargs ['para_name'] 
    parameter = kwargs ['parameter'] 

    # graph_evaluation_procedure(obj,**kwargs)    

    # obj.get_label_submeshes()    

    edges = get_manual_edges(path, id)

    # area = {n:label[0].area for n,label in obj.submeshes.items()}

    directededges_parameters(path,id,edges,parameter,para_name)



