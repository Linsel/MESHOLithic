import meta_util
import sys
from Functions.exportFiles.writeTxt import write_labels_txt_file
import trimesh
import numpy as np
import pandas as pd
from scipy.spatial import KDTree

def get_close_vertex_indices_kdtree(path:str,
                                    mesh_1:str,
                                    mesh_2:str,
                                    # labels:dict,
                                    mesh_verts:np.array, 
                                    mesh2_verts:np.array, 
                                    tolerance:float=9e-1):
    """
    Find the vertex indices of mesh_verts that are within tolerance distance from any vertex in mesh2_verts
    using a KDTree for faster proximity searches.

    Params:
        path (str): path to files
        mesh_1 (str): filename of first mesh 
        mesh_2 (str): filename of second mesh 
        mesh_verts (np.array): Array of vertices from the original mesh.
        mesh2_verts (np.array): Array of vertices from the intersection mesh.
        tolerance (float): Tolerance for distance checking.

    Returns:
        Array of indices of mesh_verts that are close to mesh2_verts.
    """
    tree = KDTree(mesh2_verts)
    num_verts = len(mesh_verts)
    report_interval = len(mesh_verts) /100000
    idx_labels = {}
    # num_labels = max (labels.values())

    # Query all vertices in the mesh against the KDTree for proximity checks
    for i in range(num_verts):
        if i % report_interval == 0 and i > 0:
            print(f'{i / num_verts * 100:.2f}% of vertices processed.')

        # Query the KDTree to find the nearest distance to any intersection vertex
        dist, _ = tree.query(mesh_verts[i])

        # If the distance is less than the tolerance, add the index
        if dist < tolerance:
            idx_labels [i] = 2
        else:
            idx_labels [i] = 1
    
    # return idx_labels
    write_labels_txt_file (idx_labels, ''.join ([   path, 
                                                    mesh_1[:-4],
                                                    '-',
                                                    mesh_2[:-4]
                                                    ]))

def get_close_vertex_indices_kdtree_2(  path:str,
                                        meshname:str,
                                        labels:dict,
                                        mesh_verts:np.array, 
                                        mesh2_verts:np.array, 
                                        tolerance:float=9e-1):
    """
    Find the vertex indices of mesh_verts that are within tolerance distance from any vertex in mesh2_verts
    using a KDTree for faster proximity searches.

    Params:
        path (str): path to files
        mesh_name (str): filename of mesh 
        mesh_verts (np.array): Array of vertices from the original mesh.
        mesh2_verts (np.array): Array of vertices from the intersection mesh.
        tolerance (float): Tolerance for distance checking.

    Returns:
        Array of indices of mesh_verts that are close to mesh2_verts.
    """
    tree = KDTree(mesh_verts)
    num_verts = len(mesh2_verts)
    report_interval = len(mesh2_verts) /100000
    idx_labels = {}
    num_labels = max (labels.values())

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
    
    # return idx_labels
    write_labels_txt_file (idx_labels, ''.join ([ path, 
                                                    meshname
                                                    ]))

def main():

    path, mesh_1, mesh_2, labelfilepath, tolerance = sys.argv[1:]

    df_label = pd.read_csv(labelfilepath,skiprows=5,header=None,sep=' ',names=['a','b'],dtype=int)  

    labels = dict(zip(df_label.a, df_label.b))
    meshname = mesh_2.split('_')[0]

    tolerance = float(tolerance)
    # Example usage:
    # Create two meshes
    # mesh1 = trimesh.creation.box(extents=(1, 1, 1))
    # mesh2 = trimesh.creation.box(extents=(1, 1, 1))

    # path = '/media/linsel/Extreme Pro/3D/TEST_DATA/'
    # Load two meshes (mesh1 is the target, mesh2 is the source to align)
    # mesh = trimesh.load(f'{path}0_000_GMCF.ply')
    # mesh = trimesh.load(f"{path}0_000_GMCF_simp05.ply")

    mesh1 = trimesh.load(f'{path}{mesh_1}')
    # mesh = trimesh.load(f'{path}RF.c-7.ply')
    mesh1_verts = mesh1.vertices
    del mesh1

    # mesh2 = trimesh.load(f'{path}0_000-001_difference.ply')
    # mesh2 = trimesh.load(f'{path}RF.c-7_difference.ply')
    mesh2 = trimesh.load(f'{path}{mesh_2}')
    mesh2_verts = mesh2.vertices # get_close_vertex_indices
    del mesh2
    print('Data imported')
    # Get the vertex indices of mesh1 that are close to mesh2
    print(f'Start 1. process: labeling vertices of {mesh_1} in distance {str(tolerance)} of {mesh_2}')
    # get_close_vertex_indices_kdtree(path, mesh_1, mesh_2,labels,mesh1_verts,mesh2_verts,tolerance)
    # print('1. process ended')
    # print(f'Start 2. process: labeling vertices of {mesh_2} in distance {str(tolerance)} of {mesh_1}')    
    get_close_vertex_indices_kdtree_2(path, meshname,labels,mesh1_verts,mesh2_verts,tolerance)
    # print('2. process ended')    

if __name__ == "__main__":
    main()