# manual ChaineOperatoire
from Classes.BasicClasses import manualEdges

from prototyping.util import *
####

from Classes.BasicClasses import manualEdges

from Classes.Graph.GraphSimplification import simplify_graph,simplify_graph_iter,simplify_directed_edges
from Classes.Graph.GraphSimplification import detect_retouches,detect_retouches_iter,label_as_retouched_edge

from Classes.Graph.GraphComparison import graph_compare,graph_dictionary_compare


from Functions.EvaluateGraph import export_graph_to_json,import_json_to_graph

from Functions.exportFiles.writeTxt import write_labels_txt_file,write_links_csv_file

from Functions.EssentialEdgesFunctions import get_manual_links

# @timing
def graph_prepare_procedure (obj:manualEdges = None,
                             **kwargs):


    # linkfilepath = kwargs ['linkfilepath'] 
    
    # obj.manual_edges = get_manual_links (linkfilepath)# get_manual_edges(path, id)    

    # obj.create_manual_DiGraph()

    # obj.G = obj.DiG_manual.to_undirected()

    # graphfilepath = kwargs ['graphfilepath'] 

    # with open(graphfilepath, 'r') as file:
    #         data = json.load(file)
    # print(data)
    # # Create a NetworkX graph
    # obj.G = nx.node_link_graph(data)

    graphfilepath = kwargs ['graphfilepath'] 
    obj.G = import_json_to_graph(graphfilepath)


def graph_simplification_procedure(obj:manualEdges = None,
                                     **kwargs):

    graph_prepare_procedure (obj,**kwargs)

    obj.path = kwargs ['path']
    obj.id = kwargs ['id']
    obj.preprocessed = kwargs ['preprocessed']
    obj.linkfilepath = kwargs ['linkfilepath']

    if 'param' not in kwargs.keys():
        param = None
    else:    
        param = kwargs ['param']

    if 'tresh' not in kwargs.keys():
        tresh = None
    else:    
        tresh = kwargs ['tresh']

        
    high_low = kwargs ['high_low']

    obj.G_simp = simplify_graph(obj.G,param, tresh, high_low)

    G1_matrix, G2_matrix, difference = graph_compare (obj.G,
                                                      obj.G_simp)

    difference.to_csv(''.join([obj.path,
                               obj.id,
                               '_G-simp-diff',
                               '.csv']))    

    
    edges_simp = simplify_directed_edges (obj.G_simp.nodes, obj.linkfilepath)

    write_links_csv_file (edges_simp, ''.join([obj.path,obj.id,'_links-simp']))    

    export_graph_to_json(obj.G_simp, ''.join([obj.path,obj.id,obj.preprocessed,'_G-simp.json'])) 
   
def retouch_edge_procedure(obj:manualEdges = None,
                                     **kwargs):

    """
    Process to detect and update ridge labeled vertices with amount of cancelled nodes between them.

    """

    graph_prepare_procedure (obj,**kwargs)

    obj.path = kwargs ['path']
    obj.id = kwargs ['id']

    if 'param' not in kwargs.keys():
        param = None
    else:    
        param = kwargs ['param']

    if 'tresh' not in kwargs.keys():
        tresh = None
    else:    
        tresh = kwargs ['tresh']


    obj.retouch_edge = detect_retouches (obj.G,param,tresh)

    retouch_edge_dict = {str(edge):vals for edge,vals in obj.retouch_edge.items()}

    with open(''.join([ obj.path,
                        obj.id,
                        '_retouch-edge',
                        '.json']), 'w') as json_file:
        json.dump(retouch_edge_dict, json_file)

    labels = label_as_retouched_edge (obj.segments_dict,obj.retouch_edge, obj.segment_label_dict)

    write_labels_txt_file (labels, ''.join([obj.path,obj.id,'_retouch-edge']))                                               

##############################


def graph_simplification_iterator_procedure (obj:manualEdges = None,
                                     **kwargs):

    obj.path = kwargs ['path']
    obj.id = kwargs ['id']

    param = kwargs ['param']
    tresh = kwargs ['tresh']
    high_low = kwargs ['high_low']
    iterations = kwargs ['iterations']

    obj.G_simp = simplify_graph(obj.G,param, tresh, high_low)

    G1_matrix, G2_matrix, difference = graph_compare (obj.G,
                                                      obj.G_simp)

    difference.to_csv(''.join([obj.path,
                               obj.id,
                               '_simp_G_dif',
                               '.csv']))

    detect_retouches_iter (G,param,tresh,2)

    [RE['retouched_edges'] for RE in retouched_edges.values()]
    
    G_iter_mat, G_iter_diff = graph_dictionary_compare(G_iter)

    girvan_newman(G,param,tresh, high_low)