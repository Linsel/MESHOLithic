import sys
import os
currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
pparentdir = os.path.dirname(parentdir)
sys.path.insert(0, currentdir) 
sys.path.insert(0, parentdir) 
sys.path.insert(0, pparentdir) 

import meta_util

# from close_vertex_idx import *
from minions.LabelMinions  import region_growing
from minions.MeshMonitoringMinions import * 

def main():

    path, mesh_1, mesh_2, labelfilepath,nodesfilepath, tolerance, dist_thres = sys.argv[1:]

    # Importing labelfile and nodesfile of mesh_1 
    df_label = pd.read_csv(labelfilepath,skiprows=5,header=None,sep=' ',names=['a','b'],dtype=int)  
    labels = dict(zip(df_label.a, df_label.b))
    df_nodes = pd.read_csv(nodesfilepath,sep=',') 

    # Add index names
    meshname2 = mesh_2.split('_')[0]
    meshname1 = mesh_1.split('_')[0]
    meshname1 = f'{meshname1}-diff'

    tolerance = float(tolerance)
    dist_thres = float(dist_thres)

    # Load two meshes (mesh1 is the previous state of mesh, mesh2 is the next state of the same object.)

    mesh1 = trimesh.load(f'{path}{mesh_1}')
    mesh1_verts = mesh1.vertices
    
    del mesh1

    mesh2 = trimesh.load(f'{path}{mesh_2}')
    mesh2_verts = mesh2.vertices # get_close_vertex_indices
    mesh2_edges = mesh2.edges
    mesh2_neighbors = mesh2.vertex_neighbors
    del mesh2

    
    print('Data imported')

    # Label mesh2 vertices with mesh1 vertex labels and label vertex with a distance greater than ´tolerance´
    # with new label (n+1).
    print(f'Start process: labeling vertices of {mesh_1} in distance {str(tolerance)} of {mesh_2}') 

    idx_labels,df_nodes_label,distance = get_close_vertex_indices_label_distance (path,meshname2,labels,df_nodes,mesh1_verts,mesh2_verts,tolerance)

    separated_label, df_nodes_separated = create_separated_label_nodes(idx_labels,df_nodes_label,mesh2_verts,mesh2_edges)
    grown_label = region_growing(path,meshname2,mesh2_verts,mesh2_edges,mesh2_neighbors,distance,separated_label,dist_thres,2)#)

    # Creates of the innitial label a newly labeled file with separately labeled connected components 
    final_label,df_final_nodes_label = create_final_label_nodes (grown_label,df_nodes_separated,mesh2_verts,mesh2_edges)

    export_final_label_nodes(path,meshname2,final_label,df_final_nodes_label)


    # Create feature vector with vertex distance between mesh2 to mesh1 vertices.
    # func_vals =  get_close_vertex_indices_kdtree_distance(mesh1_verts,mesh2_verts)

    # export funcvals 
    # write_func_vals_file (  func_vals, 
    #                         ''.join ([  path, 
    #                                     meshname,
    #                                     '_dist'
    #                                     ])
    #                         )



    # Label mesh1 vertices with a distance greater than ´tolerance´ with new label (n+1).
    # get_close_vertex_indices_kdtree_label(path,meshname1,labels,df_nodes,mesh2_verts,mesh1_verts,tolerance)
    # Create feature vector with vertex distance between mesh1 to mesh2 vertices.
    # get_close_vertex_indices_kdtree_distance(path,meshname,mesh2_verts,mesh1_verts)
    print('Process ended.')

if __name__ == "__main__":
    main()