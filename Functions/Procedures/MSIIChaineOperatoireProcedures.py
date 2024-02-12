import os,sys

currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from util import *

# compare two operational sequences 
from Functions.EvaluateGraph import evaluate_directed_edges

from Functions.EssentialEdgesFunctions import get_manual_edges,export_links,export_links_eval

# import timing function decorator  
from Functions.EssentialDecorators import timing

@timing
def CO_prepare_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelname = kwargs ['labelname']
    exp_path = kwargs ['exp_path'] 

    # Data import and data preparation 
    obj.prep_polygraphs(path,id,preprocessed,labelname,exp_path)
    obj.prep_ridges()

    # create node coordinates
    obj.get_centroids()


@timing
def MSII_procedure (obj,**kwargs):

    # path = kwargs ['path'] 
    # id = kwargs ['id']
    # preprocessed = kwargs ['preprocessed']
    # labelname = kwargs ['labelname']
    # exp_path = kwargs ['exp_path'] 
    diameter = kwargs ['diameter'] 
    n_rad = kwargs ['n_rad'] 


    # Chaine operatoire preparation
    CO_prepare_procedure(obj,**kwargs)

    # get polylines
    obj.edges_to_polygraphs()
    obj.polygraphs_to_polylines()


    # prepare for creating MSII1D_Pline object 
    obj.create_normals_vertices()
    obj.create_dict_mesh_info()
    obj.prepare_polyline()

    #create MSII1D_Pline object and calculate the MSII-1D  
    obj.polygraphs_to_graph()

    obj.calc_II_new_sphere (diameter,n_rad)
    obj.get_feature_vectors()

@timing
def MSII_feature_vector_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    graphname = kwargs ['graphname'] 
    n_rad = kwargs ['n_rad']

    MSII_procedure(obj,**kwargs)
    
    edges = get_manual_edges(path, id)

    edgeseval_rel_dict = {}
    eval_rel_betweenness_dict = {}
    DiG_ridges_edges = {}


    for n in range(0,n_rad):

        obj.segment_pline_selected_radius(n)

        obj.segment_to_graph_MSII()

        obj.ridge_pairs()

        obj.direct_ridgegraph()

        obj.get_G_ridge_properties()

        obj.get_DiG_ridge_properties(graphname)

        ridgepairs = {  ridge:values['bigger_smaller'] * values['difference'] 
                      
                        for ridge,values in obj.ridges_pairs.items() 
                            if values ['bigger_smaller'] != 0.0
                    }

        print(ridgepairs)

        DiG_ridges_edges [n] = set(obj.DiG_ridges[graphname].edges)

        edges_turned = {(edge[1],edge[0]) for edge in edges}

        evaluate_directed_edges(DiG_ridges_edges [n],edges_turned)

        evaluate_directed_edges(DiG_ridges_edges [n],edges)

        evaluate_directed_edges(edges_turned,DiG_ridges_edges [n])

        evaluate_directed_edges(edges,DiG_ridges_edges [n])

    
