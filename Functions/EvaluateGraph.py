from util import *

from Functions.exportFiles.writeTxt import write_links_csv_file, write_links_eval_csv_file
import json
from networkx.readwrite import json_graph

# compare two directed edge sets 
def evaluate_directed_edges (GT,RES):

    """
    Determines the rightly and wrongly determined directions of directed edges.

    Parameters
    ------------
    GT: set 
        Ground truth set, which is considered to be true.
    RES: set 
        Result set of edges which get compared to GT set.

    Returns
    ------------

    eval_edge_direction: dict
        Dictionary of edges, which are either be correctly (1) or incorrectly (0) directed 

    accuracy: float
        Accuracy of RES edges (1) 

    """

    # dictionary of edges, which are either be correctly (1) or incorrectly (0) directed
    eval_edge_direction = {str(edge):(1 if edge in RES else 0) for edge in GT}

    # count of correctly directed edges (1) 
    eval_para_sum = sum([val for val in eval_edge_direction.values() if val == 1])
    # count of incorrectly directed edges (1)     
    eval2_para_sum = sum([1 for val in eval_edge_direction.values() if val == 0])

    # accuracy of RES edges (1) 
    accuracy = sum([val for val in eval_edge_direction.values() if val == 1])/ (eval_para_sum + eval2_para_sum)

    # print('Right positve {}, Wrong negative: {}; Ratio: {}'.format(eval_para_sum,eval2_para_sum,accuracy))    

    return eval_edge_direction, accuracy

def less_equal_greater (edges,para,case):

    if case == 'less':
        return {edge
                    if para [edge[0]] < para [edge[1]] 
                    else 
                (edge[1],edge[0])

                for edge in edges}
    
    if case == 'equal':
        return {edge
                    if para [edge[0]] == para [edge[1]] 
                    else 
                (edge[1],edge[0])

                for edge in edges}
    
    if case == 'greater':
        return {edge
                    if para [edge[0]] > para [edge[1]] 
                    else
                (edge[1],edge[0])

                for edge in edges}

def export_links (links,*args):

    write_links_csv_file (links, ''.join ([args[0],
                                           ''.join([arg for arg in args[1:]]),
                                            '-links'
                                            ]))
    
def export_links_eval (eval,*args):

    write_links_eval_csv_file (eval, ''.join ([args[0],
                                               ''.join([arg for arg in args[1:]]),
                                                '-eval-links'
                                            ]))

def convert_sets(obj):
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, dict):
        return {k: convert_sets(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_sets(i) for i in obj]
    else:
        return obj       

def directed_edges_parameters (path,id,edges,para,para_name):

    cases = ['less','equal','greater']

    # compare_edges = {case:less_equal_greater (edges,para,case) for case in cases}

    eval_edge_directions = {}

    print(edges,para.keys())

    for case in cases:

        compare_edges = less_equal_greater (edges,para,case) 
        
        edge_direction, accuracy = evaluate_directed_edges (edges, compare_edges)
 
        args = [path,'_'.join([id,para_name,case,'acc-{}'.format(str(round(accuracy,2)))])]

        export_links (compare_edges,*args)

        export_links_eval (edge_direction,*args)

        eval_edge_directions[case] = {'accuracy':accuracy,'edges':list(compare_edges),'case':case,'edge_direction':list(edge_direction)}

    return eval_edge_directions

def direct_edges_w_parameter (path,id,preprocessed,edges,para,para_name):

    cases = ['less','equal','greater']

    for case in cases:

        compare_edges = less_equal_greater (edges,para,case) 
 
        args = [path,id,preprocessed,para_name,'_',case]

        export_links (compare_edges,*args)

def direct_edges_w_phase (path,id,preprocessed,edges,para,para_name):

    case = 'less'

    compare_edges = less_equal_greater (edges,para,case) 

    args = [path,id,preprocessed,para_name]

    export_links (compare_edges,*args)

# def export_graphs_json(G, fname):
    
#     json.dump(dict(nodes=[[n, G.nodes[n]] for n in G.nodes()] #,
#                    #edges=[[u, v, G.edge[u][v]] for u,v in G.edges()]
#                    ),
#               open(fname, 'w'), indent=3)

def export_graphs_json(G, fname):
    
    json.dump(dict(nodes=[[n, G.nodes[n]] for n in G.nodes()],
                   edges=[[u, v] for u,v in G.edges()]),
              open(fname, 'w'), indent=3)    


#####################################################


def import_json_to_graph(json_file_path):
    """
    Imports a JSON file as a NetworkX graph and handles list attributes for nodes and links.
    Assumes attributes are either directly available or need conversion from lists.

    Parameters:
        json_file_path (str): The path to the JSON file.

    Returns:
        G (networkx.Graph): A NetworkX graph created from the JSON data with attributes.
    """
    # Load the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Create an empty graph
    G = nx.Graph()

    # Add nodes
    for node in data['nodes']:
        node_id = node['id']
        # Any extra attributes associated with the node
        attributes = {k: v for k, v in node.items() if k != 'id'}
        G.add_node(node_id, **attributes)

    # Add links (edges)
    for link in data['links']:
        source = link['source']
        target = link['target']

        attributes = {k: v for k, v in link.items() if k not in ['source', 'target']}

        G.add_edge(source, target, **attributes)

    return G


##############################
def convert_numpy_types(data):
    """
    Recursively convert numpy data types to native Python data types.

    Parameters:
        data (dict or list): The data to convert.

    Returns:
        The converted data.
    """
    if isinstance(data, dict):
        return {k: convert_numpy_types(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_types(i) for i in data]
    elif isinstance(data, (np.integer, np.int64)):
        return int(data)
    elif isinstance(data, (np.floating, np.float64)):
        return float(data)
    else:
        return data


def export_graph_to_json(G, output_file_path):
    """
    Exports a NetworkX graph to a JSON file.

    Parameters:
        G (networkx.Graph): The NetworkX graph to export.
        output_file_path (str): The path where the JSON file will be saved.
    """
    # Convert the graph to node-link data format (suitable for JSON serialization)
    data = json_graph.node_link_data(G)

    data = convert_numpy_types(data)

    # Write the JSON data to a file
    with open(output_file_path, 'w') as file:
        json.dump(data, file, indent=4)

    print(f"Graph exported successfully to {output_file_path}")