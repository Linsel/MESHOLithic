import networkx as nx
import json

def get_basic_graph_properties(G):

    dict_degree = dict(G.degree)

    dict_degree_weigthed = dict(G.degree(weight='weight'))    

    dict_betweenness_centrality = nx.betweenness_centrality(G, endpoints=True,normalized=True)


    properties = {edge:{'degree':dict_degree[edge], 
                        'degree_weigthed':dict_degree_weigthed[edge], 
                        'betweenness_centrality' : dict_betweenness_centrality[edge]} 
                            for edge in dict_degree.keys()}
    
    return properties

def load_multigraph_with_edges(segments_file_path):

    # Load the graph segments (edges)
    with open(segments_file_path, 'r') as f:
        segments_data = json.load(f)
    
    # Create a multigraph object using networkx (allows parallel edges)
    DiG = nx.MultiDiGraph()
        
    # Add edges from segments data and their attributes
    for edge_id, edge_info in segments_data.items():
        source = edge_info['edge'][0]
        target = edge_info['edge'][1]
        nodes = edge_info.get('nodes', [])
        length = edge_info.get('length', 0)
        
        # Add edge with attributes (allowing parallel edges)
        DiG.add_edge(source, target, id=edge_id, nodes=nodes, length=length)
    
    return DiG