from collections import Counter
import pandas as pd
import numpy as np
import networkx as nx

from Functions.EssentialEdgesFunctions import get_manual_links

def simplify_directed_edges (nodes, linkfilepath):

    edges = get_manual_links (linkfilepath)

    edges_simp = {e for e in edges if e[0] in nodes and e[1] in nodes}

    return edges_simp

# simplify graph once by parameter
def simplify_graph (G: nx.Graph,
                    param:dict = None, 
                    tresh:float = None,
                    high_low:int = None
                    ) -> nx.Graph:

    '''
    Simplifying Graph by high-/low-pass filtering nodes according to parameter (param) and threshold (tresh). 
    "high_low" specifies values type of threshold (high- (0) or low-pass (1) filter). 
    Default is a high-pass filtering of nodes with degree <= 2.

    Args:
        G (nx.Graph):       undirected Graph
        param (dict):       filtering parameter; default: G.degree.
        tresh (float):      threshold of filter; default: 2.
        high_low (int):     selecting high- (0) oder low-pass (1) filtering; default: 0 = high-pass filter.

    Returns:      
        G_sub (nx.Graph):   simplified nx.Graph.
    '''

    if param == None:
        param = G.degree
    if tresh == None:
        tresh = 2.
    if high_low == None:
        high_low = 0     

    
    if high_low == 0:
        to_keep = [i for i,j in param if j > tresh]
    
    elif high_low == 1:
        to_keep = [i for i,j in param if j < tresh]

    print(len([i for i,j in param]),len(to_keep))

    G_sub = G.subgraph(to_keep)

    # Transfer node attributes
    for node in G_sub.nodes():
        G_sub.nodes[node].update(G.nodes[node])

    # Transfer edge attributes
    for edge in G_sub.edges():
        G_sub.edges[edge].update(G.edges[edge])

    print(len(G_sub.nodes()),len(G_sub.edges()))
    print(len(G.nodes()),len(G.edges()))

    return  G_sub

# simplify graph iteratively  
def simplify_graph_iter (G: nx.Graph,
                        param:dict = None, 
                        tresh:float = None,
                        high_low:int = None,
                        iterations:int = None
                        ) -> dict:

    '''
    Interatively simplifying Graph with the functions simplify_graph by high-/low-pass filtering nodes according to parameter (param) and threshold (tresh). 
    "high_low" specifies values type of threshold (high- (0) or low-pass (1) filter). 
    Default is like in simplify_graph a high-pass filtering of nodes with degree <= 2 with 2 iterations.

    Args:
        G (nx.Graph): undirected Graph
        param (dict): filtering parameter; default: G.degree (compare simplify_graph).
        tresh (float): threshold of filter; default: 2 (compare simplify_graph).
        high_low (int): selecting high- (0) oder low-pass (1) filtering; default: 0 = high-pass filter (compare simplify_graph).
        iterations (int): Iterations of Graph simplifications; default: 2.
    
    Returns:
        G_sub_iter (collections.Counter): dictionary including steps of simplification (keys) and simplified nx.Graph "G_sub" (values).
    '''

    if iterations == None:
        iterations = 2

    G_sub_iter = {}

    G_sub_iter [0] = G

    i = 1
    
    while i < iterations:

        G_sub_iter [i] = simplify_graph (G_sub_iter[i-1],param,tresh,high_low)
        
        i += 1

    return G_sub_iter

# adjusted graph simplification to identify edges, which are retouched with only isolated fine retouches.
# more complex scar pattens can be iteratively analysed. 
def detect_retouches (G: nx.Graph,
                        param:dict = None, 
                        tresh:float = None) -> Counter:
    
    '''
    Detects retouched edges of lithic artifact by simplifying Graph with low-pass filtering nodes according to parameter (param) and threshold (tresh).  
    Default is a low-pass filtering of nodes with degree <= 2.

    Args:
        G (nx.Graph): undirected Graph
        param (dict): filtering parameter; default: G.degree.
        tresh (float): threshold of filter; default: 2.

    Returns:
        retouch_edge (collections.Counter): returns edges with the highes number of removed scars.
    '''

    if param == None:
        param = G.degree
    if tresh == None:
        tresh = 2    

    to_remove = [i for i,j in param if j <= tresh]

    adj_nodes = {i:tuple([j for j in G[i]]) for i in to_remove}

    adj_list = [vals for vals in adj_nodes.values()]

    retouch_edge = Counter(adj_list)

    return retouch_edge

def detect_retouches_iter (G: nx.Graph,
                           param:dict = None, 
                           tresh:float = None,
                           iterations:int = None) -> dict:
    '''
    Uses an iterational approaches to detect more complex retouched edges of lithic artifact by simplifying Graph with low-pass filtering nodes according to parameter (param)
    and threshold (tresh).       
    Default is a low-pass filtering of nodes with degree <= 2.

    Args:
        G (nx.Graph): undirected Graph
        param (dict): filtering parameter; default: G.degree (compare detect_retouches).
        tresh (float): threshold of filter; default: 2 (compare detect_retouches).
        iterations (int): iterations of Graph simplifications; default: 2.

    Returns:
        G_retouch_edges (dict): dictionary containing number of iterations and nested dictionary (values) with the values 
                                                    - 'G': simplified graphs 
                                                    - 'retouched_edges': edges with the highes number of removed scars (collections.Counter).
    '''

    if iterations == None:
        iterations = 2    


    G_retouch_edges = {0:{'G':               simplify_graph (G,param,tresh,0), 
                          'retouched_edges': detect_retouches(G,param,tresh)}}          

    for i in range(1,iterations):

        G_retouch_edges [i] = {'G':               simplify_graph(G_retouch_edges[i-1]['G'],param,tresh,0), 
                               'retouched_edges': detect_retouches(G_retouch_edges[i-1]['G'],param,tresh)}

    return G_retouch_edges


def label_as_retouched_edge (segments_dict,retouch_edge,segment_label_dict):

    """
    Update exchange ridge label dictionary with amount of canceled nodes between them.  

    """


    ridge_label_edge = {vals['edge']: key for key, vals in segments_dict.items()}

    retouch_ridge_label = {edge:vals for edge,vals in retouch_edge.items()}

    labels_filtered = {vals:retouch_ridge_label[key] if key in retouch_ridge_label.keys() else retouch_ridge_label[(key[1],key[0])]  
    
                            for key,vals in ridge_label_edge.items() 
                            
                                if key in retouch_ridge_label.keys() or (key[1],key[0]) in retouch_ridge_label.keys() } 

    labels = {n: labels_filtered[label] 
                    for n,label in segment_label_dict.items() 
                        if label in labels_filtered.keys() }

    return labels

    # if iterations == None:
    #     iterations = 2

    # G_sub_iter = {}

    # G_sub_iter [0] = G

    # i = 1
    
    # while i < iterations:

    #     G_sub_iter [i] = simplify_graph (G_sub_iter[i-1],param,tresh,high_low)
        
    #     i += 1

    # return G_sub_iter