from collections import Counter
import pandas as pd
import numpy as np
import networkx as nx

from GraphToMatrix import from_G_to_node_matrix

##############################################################################
# Graph compare

# get differences in node parameters of two graphs
def graph_compare (G1:nx.Graph, 
                   G2:nx.Graph):
    
    '''
    Creates from two dependent graphs (G2 dependent from G1) a node parameter matrix and calculates the differences. 
    Node parameter matrix has a 5 (network parameters) x len(G1.nodes) shape.

    The node parameters are 

        - Degree Centrality
        - Betweenness Centrality
        - Closeness Centrality
        - Eigenvector Centrality
        - Clustering Coefficient

    Args:
        G1 (nx.Graph): Undirected Graph
        G2 (nx.Graph): simplified undirected G        

    Returns:
        G1_matrix (pd.DataFrame): 5 x len(G1.nodes) matrix of G1's node parameters
        G2_matrix (pd.DataFrame): 5 x len(G1.nodes) matrix of G2's node parameters. If node was removed, parameter is set to 0.
        difference (pd.DataFrame): Differences of G1_matrix to G2_matrix
    '''    

    # Define the size of the matrix
    m = len(G1.nodes)  # Predefined size (columns)    
    n = 5  # Number of parameters (rows)

    # G1 node network parameter matrix
    G1_matrix = from_G_to_node_matrix(G1, m, n)

    # G2 node network parameter matrix
    G2_matrix = from_G_to_node_matrix(G2, m, n)

    difference = G1_matrix - G2_matrix

    return G1_matrix, G2_matrix, difference

# get differences in node parameters of interatively simplified Graph dictionary
def graph_dictionary_compare (G_dict:dict):
    
    '''
    Creates from a G_Dict dicionary of all node parameter matrices and calculates the differences betweenn them (n - n-1). 
    Node parameter matrices have a 5 (network parameters) x len(G[0].nodes) shape.

    The node parameters are 

        - Degree Centrality
        - Betweenness Centrality
        - Closeness Centrality
        - Eigenvector Centrality
        - Clustering Coefficient

    Args:
        G_dict (dictionary): dictionary containing graph id (key) and undirected Graph (value).

    Returns:
        G_dict_matrix (dict): dictionary containing graph id (key) and pd.DataFrame (values) with 5 x len(G1.nodes) matrix as of graph node parameters.
    ''' 

    # Define the size of the matrix
    m = len(G_dict[0].nodes)  # Predefined size (columns)    
    n = 5  # Number of parameters (rows)

    # Create node network parameter matrices in dictionary
    G_dict_matrix = {key:from_G_to_node_matrix(G, m, n) for key,G in G_dict.items()}

    differences = {key:G_dict_matrix[key-1] - G_dict_matrix[key] for key,G in G_dict.items() if key != 0} 

    return G_dict_matrix, differences
