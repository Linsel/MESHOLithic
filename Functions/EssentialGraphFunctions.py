import networkx as nx

def get_basic_graph_properties(G):

    dict_degree = dict(G.degree)

    dict_degree_weigthed = dict(G.degree(weight='weight'))    

    dict_betweenness_centrality = nx.betweenness_centrality(G, endpoints=True,normalized=True)


    properties = {edge:{'degree':dict_degree[edge], 
                        'degree_weigthed':dict_degree_weigthed[edge], 
                        'betweenness_centrality' : dict_betweenness_centrality[edge]} 
                            for edge in dict_degree.keys()}
    
    return properties