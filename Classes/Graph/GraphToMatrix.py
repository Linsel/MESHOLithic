from collections import Counter
import pandas as pd
import numpy as np
import networkx as nx

# functions to creating matrices of Graphs
def from_G_to_node_matrix (G:nx.Graph,
                          m:int,
                          n:int):

    """
    Creates and sizes a matrix representing node parameters in a graph.
            This function first generates a matrix of node parameters for the  given graph `G`. 
            Then, it sizes this matrix to the specified dimensions `m` and `n`.

    Args:
        G (nx.Graph): graph object whose node parameters are to be represented in the matrix.
        m (int): nrows of output matrix.
        n (int): ncols of output matrix.

    Returns:
        G_node_matrix_filled (pd.DataFrame): array representing the node parameters mxn matrix of graph G

    """

    # G node network parameter matrix
    G_node_matrix = get_node_parameter_matrix(G)

    G_node_matrix_filled = resize_matrix(G_node_matrix, m, n)

    return G_node_matrix_filled

def get_node_parameter_matrix (G:nx.Graph):

    """
    Generates a matrix of 5 node parameters for a given graph.

    Args:
        G (nx.Graph): nx.Graph object for which node parameters are calculated.

    Returns:
        node_parameter_matrix (pd.DataFrame):   pd.DataFrame where nodes are rows and columns are node parameters (centrality measures 
                                                and clustering coefficient).

    """    
    
    # Calculating various centrality measures and clustering coefficient
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    closeness_centrality = nx.closeness_centrality(G)
    eigenvector_centrality = nx.eigenvector_centrality(G)
    clustering_coefficient = nx.clustering(G)

    # Creating a pd.DataFrame
    node_parameter_matrix = pd.DataFrame({
        'Degree Centrality': degree_centrality,
        'Betweenness Centrality': betweenness_centrality,
        'Closeness Centrality': closeness_centrality,
        'Eigenvector Centrality': eigenvector_centrality,
        'Clustering Coefficient': clustering_coefficient
    })

    return node_parameter_matrix

def resize_matrix(node_matrix: pd.DataFrame, 
                m: int, 
                n: int):

    """
    Resizes a given matrix to a specified size with zero-filling.

    This function resizes the input `node_matrix` to mxn matrix. Resized matrix is zero-filled where new cells are created.

    Args:
        G (nx.Graph): graph object whose node parameters are to be represented in the matrix.
        m (int): nrows of output matrix.
        n (int): ncols of output matrix.

    Returns:
        matrix (pd.DataFrame): resized pd.DataFrame with dimensions mxn, zero-filled as necessary.

    Raises:
        ValueError: ncols in `node_matrix` does not match n.

    """

    # Ensure that n matches the number of columns in node_matrix
    if n != node_matrix.shape[1]:
        print(node_matrix.shape[1])
        print(n)
        raise ValueError("The number of parameters (n) must match the number of columns in the node matrix.")

    # Create a zero-filled matrix of size m x n
    matrix = pd.DataFrame(np.zeros((m, n)), columns=node_matrix.columns)

    # Adjust the row IDs to start from 1
    matrix.index = matrix.index + 1    

    # Data input from node_matrix
    for name, values in node_matrix.iteritems():
        for ind in node_matrix.index:
            matrix [name][ind] = values[ind]

    return matrix
