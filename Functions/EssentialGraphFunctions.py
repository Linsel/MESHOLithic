import networkx as nx

def get_basic_graph_properties(graph):

    dict_degree = dict(graph.degree)

    dict_degree_weigthed = dict(graph.degree(weight='weight'))    

    dict_betweenness_centrality = nx.betweenness_centrality(graph, endpoints=True,normalized=True)


    properties = {edge:{'degree':dict_degree[edge], 
                        'degree_weigthed':dict_degree_weigthed[edge], 
                        'betweenness_centrality' : dict_betweenness_centrality[edge]} 
                            for edge in dict_degree.keys()}
    
    return properties