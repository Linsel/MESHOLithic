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
from Functions.PolylineGraph import ridge_inside_mean_curv, filter_metadata,get_vertices_in_radius,ridge_inside_angle_normals#ridge_outside_mean_curv

@timing
def CO_prepare_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelfilepath = kwargs ['labelfilepath']

    # Data import and data preparation 
    obj.prep_polygraphs(path,id,preprocessed,labelfilepath)
    obj.prep_ridges()

    # create node coordinates
    # obj.get_centroids()
    

@timing
def MSII_procedure (obj,**kwargs):

    diameter = kwargs ['diameter'] 
    n_rad = kwargs ['n_rad'] 
    obj.nrad = n_rad
    print('done (1/7)')   
    # Chaine operatoire preparation
    CO_prepare_procedure(obj,**kwargs)
    print('CO_prepare_procedure done (2/7)')   
    # get polylines
    obj.edges_to_polygraphs()
    obj.polygraphs_to_polylines()
    print('done (3/7)')   

    # prepare for creating MSII1D_Pline object 
    obj.create_normals_vertices()
    obj.create_dict_mesh_info()
    obj.prepare_polyline()
    print('done (4/7)')   
    #create MSII1D_Pline object and calculate the MSII-1D  
    obj.polygraphs_to_graph()
    print('done (5/7)')   
    obj.calc_II_new_sphere (diameter,n_rad)
    print('done (6/7)')      
    obj.get_feature_vectors()

@timing
def MSII_feature_vector_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    graphname = kwargs ['graphname'] 
    n_rad = kwargs ['n_rad']

    MSII_procedure(obj,**kwargs)
    
    print(path,id)

    edges = get_manual_edges(path, id)

    # edgeseval_rel_dict = {}
    # eval_rel_betweenness_dict = {}
    DiG_ridges_edges = {}


    for n in range(0,n_rad):

        obj.segment_pline_selected_radius(n)

        obj.segment_to_graph_MSII()

        obj.ridge_pairs()

        obj.direct_ridgegraph()

        obj.get_G_ridge_properties()

        obj.get_DiG_ridge_properties(graphname)

        try:

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

        except:
            print(id)

def CO_concavity_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    max_rad = kwargs ['max_rad'] 
    parameters = kwargs ['parameters'] 
    n_rad = kwargs ['n_rad'] 
    obj.graphname = kwargs ['graphname']

    CO_prepare_procedure(obj,**kwargs)

    # # Data import and data preparation 
    # obj.prep_polygraphs(path,id,preprocessed,labelfilepath)

    # # Create 
    # obj.prep_ridges()
    # obj.extract_ridges()    

    # create node coordinates
    # obj.get_centroids()

    # get polylines
    obj.edges_to_polygraphs()
    obj.polygraphs_to_polylines()


    # prepare for creating Pline object 
    obj.create_normals_vertices()
    obj.create_dict_mesh_info()
    obj.prepare_polyline()

    # extract parameters, which are important to calculate CO concavity  


    dict_label = obj.dict_label
    label_outline_vertices = obj.label_outline_vertices
    neighs = obj.ridge_neighbour_notshared_label  

    metadata = filter_metadata (obj.metadata ['ply_raw']['vertex']['data'],
                                parameters)
    
    for r in range(1,2**n_rad+1):

        rad = max_rad*r/n_rad

        obj.label_arr = get_vertices_in_radius (obj.vertices,
                                                obj.kdtree,
                                                label_outline_vertices,
                                                neighs,
                                                dict_label,
                                                rad,
                                                metadata)     

        obj.label_arr_mean = ridge_inside_mean_curv(path,id,preprocessed,r,dict_label,obj.label_arr)

        obj.max_func_val = {vert:np.float32(max_f) for vert, values in obj.label_arr_mean.items() for max_f in values.values()}

        param_name = '_'.join (['-'.join(['CO',
                                             'concavity',
                                            'r{rad:.2f}'
                                             ])]) 

        obj.export_max_func_val(param_name)

        # obj.evaluate_label_arr_mean()

def CO_angle_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    max_rad = kwargs ['max_rad'] 
    parameters = kwargs ['parameters'] 
    n_rad = kwargs ['n_rad'] 
    obj.graphname = kwargs ['graphname']

    CO_prepare_procedure(obj,**kwargs)

    # # Data import and data preparation 
    # obj.prep_polygraphs(path,id,preprocessed,labelfilepath)

    # # Create 
    # obj.prep_ridges()
    # obj.extract_ridges()    

    # create node coordinates
    # obj.get_centroids()

    # get polylines
    obj.edges_to_polygraphs()
    obj.polygraphs_to_polylines()


    # prepare for creating Pline object 
    obj.create_normals_vertices()
    obj.create_dict_mesh_info()
    obj.prepare_polyline()

    # extract parameters, which are important to calculate CO concavity  


    dict_label = obj.dict_label
    label_outline_vertices = obj.label_outline_vertices
    neighs = obj.ridge_neighbour_notshared_label  

    metadata = filter_metadata (obj.metadata ['ply_raw']['vertex']['data'],
                                parameters)
    
    for r in range(1,2**n_rad+1):

        rad = max_rad*r/n_rad

        obj.label_arr = get_vertices_in_radius (obj.vertices,
                                                obj.kdtree,
                                                label_outline_vertices,
                                                neighs,
                                                dict_label,
                                                rad,
                                                metadata)     

        obj.label_arr_mean = ridge_inside_angle_normals(path,id,preprocessed,obj.normals,r,dict_label,obj.label_arr)

        obj.max_func_val = {vert:np.float32(max_f) for vert, values in obj.label_arr_mean.items() for max_f in values.values()}

        param_name = '_'.join (['-'.join(['CO',
                                             'concavity',
                                            'r{rad:.2f}'
                                             ])]) 

        obj.export_max_func_val(param_name)


