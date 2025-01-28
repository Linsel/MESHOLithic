import os,sys

currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from util import *

# compare two operational sequences 
from Functions.EvaluateGraph import directed_edges_parameters, export_links,direct_edges_w_parameter,direct_edges_w_phase,export_graphs_json,export_graph_to_json

from Functions.EssentialEdgesFunctions import get_manual_links#get_manual_edges,export_links,export_links_eval

def prep_graph_mesh_procedure(obj,**kwargs):

    # LabelledMesh init
    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelfilepath = kwargs ['labelfilepath']

    # Data import 
    obj.load_labelled_mesh(path,id,preprocessed,labelfilepath) 
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

    return obj

def graph_undirected_procedure (obj,**kwargs):

    # LabelledMesh init
    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    # labelfilepath = kwargs ['labelfilepath']

    obj = prep_graph_mesh_procedure(obj,**kwargs)

    # # Data import 
    # obj.load_labelled_mesh(path,id,preprocessed,labelfilepath) 
    # obj.extract_ridges()

    # # get polylines
    # obj.edges_to_polygraphs()
    # obj.polygraphs_to_polylines()

    # # create node coordinates
    # obj.get_centroids()
    # # obj.get_NNs()
    # # obj.get_NNs()

    # # prepare for creating MSII1D_Pline object 
    # obj.create_normals_vertices()
    # obj.create_dict_mesh_info()
    # obj.prepare_polyline()

    # # prepare for get ridges and for scar-ridge-graph model and leading to chaine-operatoire 
    # obj.prep_ridges()
    # obj.polineline_segmenting()
    # obj.segment_to_graph()

    args = [path,id,preprocessed]

    export_links (obj.G_ridges.edges, args)

    export_graphs_json(obj.G_ridges, ''.join([path,id,preprocessed,'_G.json']))   

    export_graph_to_json(obj.G_ridges, ''.join([path,id,preprocessed,'_Graph.json'])) 


def graph_direct_procedure (obj,**kwargs):

    # LabelledMesh init
    # path = kwargs ['path'] 
    # id = kwargs ['id']
    # preprocessed = kwargs ['preprocessed']
    # labelfilepath = kwargs ['labelfilepath']

    prep_graph_mesh_procedure(obj,**kwargs)

    # scales
    radius_scale = kwargs ['radius_scale'] 
    circumference = kwargs ['circumference'] 

    # # Data import 
    # obj.load_labelled_mesh(path,id,preprocessed,labelfilepath) 
    # obj.extract_ridges()

    # # get polylines
    # obj.edges_to_polygraphs()
    # obj.polygraphs_to_polylines()

    # # create node coordinates
    # obj.get_centroids()
    # # obj.get_NNs()
    # # obj.get_NNs()

    # # prepare for creating MSII1D_Pline object 
    # obj.create_normals_vertices()
    # obj.create_dict_mesh_info()
    # obj.prepare_polyline()

    # # prepare for get ridges and for scar-ridge-graph model and leading to chaine-operatoire 
    # obj.prep_ridges()
    # obj.polineline_segmenting()
    # obj.segment_to_graph()

    obj.create_undirected_model(radius_scale,circumference)

# @timing
def graph_direct_network_parameter_procedure (obj,**kwargs):

    # LabelledMesh init
    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    linkfilepath = kwargs ['linkfilepath']

    prep_graph_mesh_procedure(obj,**kwargs)


    G_network_parameters = {
                        'degree':           dict(nx.degree(obj.G_ridges)),
                        'degree_centrality':dict(nx.degree_centrality(obj.G_ridges)),
                        'betweenness':      dict(nx.betweenness_centrality(obj.G_ridges))
                        }
    
    del obj


    # Convert the dictionary to a JSON string
    json_data = json.dumps(G_network_parameters, indent=3)

    graph_file = ''.join([path,id,'_'.join([preprocessed,'graph-params.json'])])

    # Save the JSON string to a file
    with open(graph_file, 'w') as f:
        f.write(json_data)  


    edges = get_manual_links (linkfilepath)

    eval_edge_directions = {}

    for k,v in G_network_parameters.items():

        eval_edge_directions [k] = directed_edges_parameters(path,id,edges,v,k) 

    # Convert the dictionary to a JSON string
    json_data = json.dumps(eval_edge_directions, indent=3)

    eval_file = ''.join([path,id,'_'.join([preprocessed,'graph-eval.json'])])

    # Save the JSON string to a file
    with open(eval_file, 'w') as f:
        f.write(json_data)          

# @timing
def graph_direct_parameter_procedure (obj,**kwargs):

    # LabelledMesh init
    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    # labelfilepath = kwargs ['labelfilepath']

    prep_graph_mesh_procedure(obj,**kwargs)

    # scales
    radius_scale = kwargs ['radius_scale'] 
    circumference = kwargs ['circumference'] 

    is_phase = kwargs ['is_phase'] 
    params = kwargs ['params']  

    # # Data import 
    # obj.load_labelled_mesh(path,id,preprocessed,labelfilepath) 
    # obj.extract_ridges()

    # # get polylines
    # obj.edges_to_polygraphs()
    # obj.polygraphs_to_polylines()

    # # create node coordinates
    # obj.get_centroids()
    # # obj.get_NNs()
    # # obj.get_NNs()

    # # prepare for creating MSII1D_Pline object 
    # obj.create_normals_vertices()
    # obj.create_dict_mesh_info()
    # obj.prepare_polyline()

    # # prepare for get ridges and for scar-ridge-graph model and leading to chaine-operatoire 
    # obj.prep_ridges()
    # obj.polineline_segmenting()
    # obj.segment_to_graph()


    obj.create_undirected_model(radius_scale,circumference)

    obj.export_graphs_labels()
    
    edges = obj.G_ridges.edges 

    procedures = {True: direct_edges_w_phase,
                  False: direct_edges_w_parameter}

    func = procedures.get(is_phase)

    func (path,id,preprocessed,edges,params['values'],params['name'])

    graph_export(obj,**kwargs)


# @timing
def graph_evaluate_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    para_name = kwargs ['para_name'] 
    parameter = kwargs ['parameter'] 
    linkfilepath = kwargs ['linkfilepath']  

    # graph_evaluation_procedure(obj,**kwargs)    

    # obj.get_label_submeshes()    

    edges = get_manual_links (linkfilepath)#edges = get_manual_edges(path, id)

    # area = {n:label[0].area for n,label in obj.submeshes.items()}

    directed_edges_parameters(path,id,edges,parameter,para_name)


###################
# Graph Export
def update_segment_label_dict(obj, current_dict, depth=4):
    if depth == 0:
        return current_dict
    
    # Generate the next level of neighbors and their associated segment ids
    segment_neighbours = {
        nei: [n for n in obj.vertex_neighbors_dict[nei]]
        for nei in current_dict.keys()
    }

    segment_label_dict_next = {
        n: current_dict[nei] for nei, ns in segment_neighbours.items() for n in ns
    }
    
    # Update the original dictionary with the new associations
    current_dict.update(segment_label_dict_next)
    
    # Recur to process the next level of neighbors
    return update_segment_label_dict(obj,segment_label_dict_next, depth - 1)


def graph_export (obj,**kwargs):


    # LabelledMesh init
    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    border_thickness = kwargs ['border_thickness'] 

    obj.segments_dict = {}

    n = 0
    
    for edge,nodes in obj.segments.items():

        if nodes != {'vertices': []}:
            
            obj.segments_dict [n + 1] = {'edge':edge,
                                         'nodes': [int(node) for node in nodes['vertices']],
                                         'length': int(len(nodes['vertices']))}

            n = n + 1 
            
        else:
            obj.segments_dict [n + 1] = {'edge':edge,
                                         'nodes': [],
                                         'length': 0}

            n = n + 1 
            continue

    # Convert the dictionary to a JSON string
    json_data = json.dumps(obj.segments_dict, indent=3)

    graph_file = ''.join([path,id,'_'.join([preprocessed,'graph-segments.json'])])

    # Save the JSON string to a file
    with open(graph_file, 'w') as f:
        f.write(json_data)

    export_graph_to_json(obj.G_ridges, ''.join([obj.path,obj.id,obj.preprocessed,'_G.json'])) 

    segment_label_dict = {node:s_id for s_id, segment in obj.segments_dict.items() for node in segment ['nodes']}

    # Update the segment_label_dict with neighbors up to the set up border_thickness levels deep
    obj.segment_label_dict = update_segment_label_dict(obj,segment_label_dict, border_thickness)

    segment_label = ''.join([path,id,'_'.join([preprocessed,'updated-labels-bt{}'.format(str(border_thickness))])])

    write_labels_txt_file (obj.segment_label_dict, segment_label)