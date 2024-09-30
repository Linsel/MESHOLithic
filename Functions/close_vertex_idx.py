import sys
import os
currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
pparentdir = os.path.dirname(parentdir)
sys.path.insert(0, currentdir) 
sys.path.insert(0, parentdir) 
sys.path.insert(0, pparentdir) 
# sys.path.insert(0, ''.join([pparentdir,'/minions'])) 
# sys.path.insert(0, ''.join([parentdir,'/Functions','/Procedures'])) 
import meta_util
# from Functions.exportFiles.writeTxt import write_labels_txt_file
from minions.MeshTxtMinions import write_func_vals_file,write_labels_file
from minions.MeshMinions import filter_verts
from minions.LabelMinions  import merge_small_connected_components,assign_label_to_neighbors,convert_edges_to_vertex_neighbors
import trimesh
import numpy as np
import pandas as pd
from scipy.spatial import KDTree
import networkx as nx

def connected_components_by_labels(edges, labels_dict):
    """
    Detect and label connected components for each label group using networkx.
    
    Parameters:
    - edges: list of edges (pairs of vertex indices)
    - labels_dict: dictionary of vertex: label assignments
    
    Returns:
    - vert_label: dictionary where keys are labels and values are lists of connected components (each component is a set of vertices)
    """
    # Reverse the labels dictionary to group vertices by their label
    reversed_dict = transform_to_label_verts(labels_dict)
    
    # Initialize the result dictionary for components by label
    components_by_label = {}

    # Create a NetworkX graph from the edges
    graph = nx.Graph()
    graph.add_edges_from(edges)

    # Iterate over each label and its corresponding vertices
    for label, group_vertices in reversed_dict.items():
        # Create a subgraph with only the vertices from the current label
        subgraph = graph.subgraph(group_vertices)

        # Get the connected components for this subgraph
        components = list(nx.connected_components(subgraph))

        # Store the components for this label
        components_by_label[label] = [set(component) for component in components]

    vert_label = transform_to_vert_label_dict (components_by_label)    

    return vert_label

def transform_to_label_verts(labels_dict):
    """
    Reverse the labels dictionary to group vertices by their assigned label.
    
    Parameters:
    - labels_dict: dictionary of vertex: label assignments
    
    Returns:
    - reversed_dict: dictionary where keys are labels and values are lists of vertices
    """
    reversed_dict = {}
    for vertex, label in labels_dict.items():
        if label not in reversed_dict:
            reversed_dict[label] = []
        reversed_dict[label].append(vertex)
    return reversed_dict

def transform_to_vert_label_dict(components_by_label):
    """
    Reverse the components_by_label dictionary back to a vertex: label mapping.
    
    Parameters:
    - components_by_label: dictionary where keys are labels and values are lists of sets of vertices
    
    Returns:
    - reversed_back_dict: dictionary where keys are vertices and values are their corresponding labels
    """
    reversed_back_dict = {}

    # Iterate over each label and its corresponding connected components
    for label, components in components_by_label.items():
        # Iterate over each connected component
        for component in components:
            # For each vertex in the component, assign the corresponding label
            for vertex in component:
                reversed_back_dict[vertex] = label

    return reversed_back_dict

def get_close_vertex_indices_kdtree_label(  path:str,
                                            meshname:str,                                         
                                            labels:dict,
                                            df_nodes: pd.DataFrame,
                                            mesh_verts:np.array, 
                                            mesh2_verts:np.array,
                                            # mesh2_edges:list, 
                                            tolerance:float=9e-1):
    """
    Checks if any vertex in `mesh2_verts` is within a specified distance `tolerance` from a vertex in `mesh_verts` 
    using a KDTree for efficient proximity searches. If a vertex in `mesh2_verts` is found to be close 
    to a vertex in `mesh_verts`, the label of the closest vertex from `mesh_verts` is assigned to it. 
    If no nearby vertex from `mesh_verts` is found within the distance threshold, a new label is assigned 
    to the vertex in `mesh2_verts`.

    Params:
        path (str): Path to files.
        mesh_name (str): Filename of mesh.
        labels (dict): Contains vertices (keys) and labels of mesh_verts.
        df_nodes (pd.DataFrame): DataFrame including labels and their position in operational sequence. 
        mesh2_verts (np.array): Array of vertices from the intersection mesh.
        mesh2_verts (np.array): Array of vertices from the intersection mesh.
        tolerance (float): Tolerance for distance checking.

    Returns:
        idx_labels (dict): Dictionary idx_labels .
        
    """
    tree = KDTree(mesh_verts)
    num_verts = len(mesh2_verts)
    report_interval = len(mesh2_verts) / 100000
    idx_labels = {}
    num_labels = max (labels.values())

    # Add new label node to node file
    previous_step = int(df_nodes[['phase']].max()[0])
    df_nodes.loc[len(df_nodes.index)] = [num_labels+1,previous_step+1,'','negative']


    # Query all vertices in the mesh against the KDTree for proximity checks
    for i in range(num_verts):
        if i % report_interval == 0 and i > 0:
            print(f'{i / num_verts * 100:.2f}% of vertices processed.')

        # Query the KDTree to find the nearest distance to any intersection vertex
        dist, idx = tree.query(mesh2_verts[i],k=1)


        # If the distance is less than the tolerance, add the index
        if dist < tolerance:
            idx_labels [i] = labels [idx]
        else:
            idx_labels [i] = num_labels + 1
    
    # return labels_idxs
    write_labels_file (idx_labels, ''.join ([ path, 
                                                    meshname,
                                                    '_simple-labels'
                                                    ]))    
    
    # Export new node file
    df_nodes.to_csv(''.join([   path, 
                                meshname,
                                '_simple-nodes.csv']),
                                index=False)
    
    return idx_labels,df_nodes
    
def get_close_vertex_indices_kdtree_distance (  mesh_verts:np.array, 
                                                mesh2_verts:np.array):
    """
    Finds the distance to the closest vertex of mesh_verts from any vertex in mesh2_verts using a KDTree
    for faster proximity searches.

    Params:
        path (str): Path to files.
        mesh_name (str): Filename of mesh.
        mesh_verts (np.array): Array of vertices from the original mesh.
        mesh2_verts (np.array): Array of vertices from the intersection mesh.

    Returns:
        func_vals (dict): nested dictionary includes name of the function value and its values for each vertex.
    """
    tree = KDTree(mesh_verts)
    num_verts = len(mesh2_verts)
    report_interval = len(mesh2_verts) /100000
    idx_dist = {}

    # Query all vertices in the mesh against the KDTree for proximity checks
    for i in range(num_verts):
        if i % report_interval == 0 and i > 0:
            print(f'{i / num_verts * 100:.2f}% of vertices processed.')

        # Query the KDTree to find the nearest distance to any intersection vertex
        dist, _ = tree.query(mesh2_verts[i],k=1)

        idx_dist [i] = dist

    func_vals = {'name':'distance','values':idx_dist}

    return func_vals

def create_final_label_nodes (  idx_labels:dict,
                                df_nodes: pd.DataFrame,
                                mesh2_verts:np.array,
                                mesh2_edges:list):
    """
    Checks if any vertex in `mesh2_verts` is within a specified distance `tolerance` from a vertex in `mesh_verts` 
    using a KDTree for efficient proximity searches. If a vertex in `mesh2_verts` is found to be close 
    to a vertex in `mesh_verts`, the label of the closest vertex from `mesh_verts` is assigned to it. 
    If no nearby vertex from `mesh_verts` is found within the distance threshold, a new label is assigned 
    to the vertex in `mesh2_verts`.


    Params:
        idx_labels (dict): Contains vertices (keys) and labels of mesh_verts.
        mesh_verts (np.array): Array of vertices from the original mesh.
        mesh2_verts (np.array): Array of vertices from the intersection mesh.
        mesh2_edges (list): List of edges of mesh2

    Returns:
        final_label (dict): Updated index-label dictionary.
        df_nodes (pd.DataFrame): Updated DataFrame including connected components and their position in operational sequence. 
    """
    
    num_labels = max (idx_labels.values())
    final_label = {}
    vertex_neighbors = convert_edges_to_vertex_neighbors (mesh2_edges)

    for i in range (1,num_labels + 3):

        if i != 1 and len(final_label.keys()) > 0: 
            num_labels = max (final_label.values())

        label_verts = np.array([i_vert for i_vert,label in idx_labels.items() if int(label) == i])

        if len(label_verts) == 0:
            continue

        innitial_components = filter_verts (mesh2_verts,mesh2_edges,label_verts)

        # find vertices not connected to other vertex of innitial_components
        innitial_components_verts = {v for comp in innitial_components for v in comp}
        
        # Use list comprehension to find vertices not in innitial_components_verts
        single_verts = [v for v in label_verts if v not in innitial_components_verts]       

        for j in single_verts: 
            final_label [j] = assign_label_to_neighbors (j, vertex_neighbors,idx_labels)

        try:
            components = merge_small_connected_components(innitial_components)
        except:
            components = [single_verts]
            continue

        if len (components) == 1:

            for vert in components[0]:
                final_label [vert] = i   

            continue           

        biggest_comp = max(components, key=len)
        for n,comp in enumerate(components):
            
            for vert in comp:
                if len(comp) == len(biggest_comp):
                    final_label [vert] = i  
                else:
                    final_label [vert] = num_labels + n + 1
            if n > 1:
                # df_nodes.loc[len(df_nodes.index)] = [num_labels + n + 1,df_nodes.loc[i, 'phase']]
                df_nodes.loc[len(df_nodes.index)] = [num_labels + n + 1,df_nodes.loc[i-1, 'phase'],i,df_nodes.loc[i-1, 'type']]                

    return final_label,df_nodes

def export_final_label_nodes (  path:str,
                                meshname:str,       
                                final_label:dict,
                                df_nodes:pd.DataFrame):
    """   
    Exports  final label as "_scar-labels.txt" and df_nodes as export_final_label_nodes "_nodes.csv" files if idx_labels and final_label have the same amount of vertices.

    Params:
        path (str): Path to files.
        mesh_name (str): Filename of mesh.
        idx_labels (dict): Contains vertices (keys) and labels of mesh_verts.
        final_label (dict): Updated index-label dictionary.
        df_nodes (pd.DataFrame): Updated DataFrame including connected components and their position in operational sequence. 
    
    """


    write_labels_file (final_label, ''.join ([  path, 
                                                meshname,
                                                '_scar-labels'
                                                ]))
    
    # Export new node file
    df_nodes.to_csv(''.join([   path, 
                                meshname,
                                '_nodes.csv']),
                                index=False)






# def get_close_vertex_indices_kdtree(path:str,
#                                     mesh_1:str,
#                                     mesh_2:str,
#                                     # labels:dict,
#                                     mesh_verts:np.array, 
#                                     mesh2_verts:np.array, 
#                                     tolerance:float=9e-1):
#     """
#     Find the vertex indices of mesh_verts that are within tolerance distance from any vertex in mesh2_verts
#     using a KDTree for faster proximity searches.

#     Params:
#         path (str): path to files
#         mesh_1 (str): filename of first mesh 
#         mesh_2 (str): filename of second mesh 
#         mesh_verts (np.array): Array of vertices from the original mesh.
#         mesh2_verts (np.array): Array of vertices from the intersection mesh.
#         tolerance (float): Tolerance for distance checking.

#     Returns:
#         Array of indices of mesh_verts that are close to mesh2_verts.
#     """
#     tree = KDTree(mesh2_verts)
#     num_verts = len(mesh_verts)
#     report_interval = len(mesh_verts) /100000
#     idx_labels = {}
#     # num_labels = max (labels.values())

#     # Query all vertices in the mesh against the KDTree for proximity checks
#     for i in range(num_verts):
#         if i % report_interval == 0 and i > 0:
#             print(f'{i / num_verts * 100:.2f}% of vertices processed.')

#         # Query the KDTree to find the nearest distance to any intersection vertex
#         dist, _ = tree.query(mesh_verts[i])

#         # If the distance is less than the tolerance, add the index
#         if dist < tolerance:
#             idx_labels [i] = 2
#         else:
#             idx_labels [i] = 1
    
#     # return idx_labels
#     write_labels_file (idx_labels, ''.join ([   path, 
#                                                     mesh_1[:-4],
#                                                     '-',
#                                                     mesh_2[:-4]
#                                                     ]))


# def get_updated_final_labels (  idx_labels:dict,
#                                 df_nodes: pd.DataFrame,
#                                 mesh2_verts:np.array,
#                                 mesh2_edges:list):
#     """
#     Separates labeled vertices to connected components and creates new label dictionary. 
#     Further, adds for each connected component a new entry to `df_nodes`. 

#     Params:
#         path (str): Path to files.
#         mesh_name (str): Filename of mesh.
#         idx_labels (dict): Contains vertices (keys) and labels of mesh_verts.
#         mesh_verts (np.array): Array of vertices from the original mesh.
#         mesh2_verts (np.array): Array of vertices from the intersection mesh.
#         mesh2_edges (list): List of edges of mesh2

#     Returns:
#         idx_labels (dict): Dictionary idx_labels.
        
#     """
#     num_labels = max (idx_labels.values())
#     final_label = {}
#     for i in range (1,num_labels + 1):

#         if i != 1 and len(final_label.keys()) > 0: 
#             num_labels = max (final_label.values())

#         label_verts = np.array([i_vert for i_vert,label in idx_labels.items() if int(label) == i])

#         if len(label_verts) == 0:
#             continue

#         components = filter_verts (mesh2_verts,mesh2_edges,label_verts)

#         print (len(components))

#         for n,comp in enumerate(components):
           
#             for vert in comp:
#                 if n == 1:
#                     final_label [vert] = i  
#                 else:
#                     final_label [vert] = num_labels + n + 1
#             if n > 1:
#                 df_nodes.loc[len(df_nodes.index)] = [num_labels + n + 1,df_nodes.loc[i, 'phase']]



# def create_final_label_nodes (  path:str,
#                                 meshname:str,                                         
#                                 idx_labels:dict,
#                                 df_nodes: pd.DataFrame,
#                                 mesh2_verts:np.array,
#                                 mesh2_edges:list):
#     """
#     Separates in labeled vertices to connected components and creates new label file. 
#     Further, adds for each connected component a new entry to `df_nodes` and export node file. 


#     Params:
#         path (str): Path to files.
#         mesh_name (str): Filename of mesh.
#         idx_labels (dict): Contains vertices (keys) and labels of mesh_verts.
#         df_nodes (pd.DataFrame): DataFrame including labels and their position in operational sequence. 
#         mesh2_verts (np.array): Array of vertices from the intersection mesh.
#         mesh2_edges (list): List of edges of mesh2

#     Returns:
#         idx_labels (dict): Updated `idx_labels` dictionary including connected components.
#         idx_labels (pd.DataFrame): `df_nodes` with additional connected components entries.
        
#     """
#     num_labels = max (idx_labels.values())
#     final_label = {}
#     for i in range (1,num_labels + 2):

#         if i != 1 and len(final_label.keys()) > 0: 
#             num_labels = max (final_label.values())

#         label_verts = np.array([i_vert for i_vert,label in idx_labels.items() if int(label) == i])

#         if len(label_verts) == 0:
#             continue

#         components = filter_verts (mesh2_verts,mesh2_edges,label_verts)

#         components = merge_small_connected_components(components,10)

#         if len (components) == 1:

#             for vert in components[0]:
#                 final_label [vert] = i   

#             continue           

#         # for n,comp in enumerate(components):
#         #     print(len(comp))
#         #     for vert in comp:
#         #         if len(comp) < 10:
#         #             final_label [vert] = i                  
#         #         else:
#         #             final_label [vert] = num_labels + n + 1

#         biggest_comp = max(components, key=len)
#         for n,comp in enumerate(components):
            
#             for vert in comp:
#                 if len(comp) == len(biggest_comp):
#                     final_label [vert] = i  
#                 else:
#                     print(vert)
#                     final_label [vert] = num_labels + n + 1
#             if n > 1:
#                 df_nodes.loc[len(df_nodes.index)] = [num_labels + n + 1,df_nodes.loc[i, 'phase'],i,df_nodes.loc[i, 'type']]


#     if len(idx_labels.keys()) == len(final_label.keys()):

#         write_labels_file (final_label, ''.join ([ path, 
#                                                         meshname,
#                                                         '_scar-labels'
#                                                         ]))
        
#         # Export new node file
#         df_nodes.to_csv(''.join([   path, 
#                                     meshname,
#                                     '_nodes.csv']),
#                                     index=False)
#     else:
#         print(len(idx_labels.keys()), len(final_label.keys()))

