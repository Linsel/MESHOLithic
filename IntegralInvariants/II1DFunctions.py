from util import *

import networkx as nx
# import numpy as np
# import trimesh

# graph alteration and testing functions 



def test_nodes_two_neigh(node,neigh_list):
    if len(neigh_list) > 2:
        print('{0} has more than two neighbors.'.format(node))

def create_start_list(p_list,pos_iter):
    
    # using % operator and loop
    # cyclic iteration in list
    
    p_res = []
    for i in range(len(p_list)):
        p_res.append(p_list[pos_iter % len(p_list)])
        pos_iter = pos_iter + 1
    
    return p_res

# create icospheres
def create_icospheres(radii):
    
    # icospheres = np.array([trimesh.creation.icosphere(radius=r) for r in radii]) + origin 
    icospheres = np.array([trimesh.creation.icosphere(radius=r) for r in radii])

    return icospheres

# MSII parameter
def angle_neighbours(newPoint,centerPoint,oldPoint):

    # Calculate the two vectors from centerPoint
    vector1 = newPoint - centerPoint
    vector2 = oldPoint - centerPoint

    # Calculate the cross product of the two vectors to get the rotation axis
    rotation_axis = np.cross(vector1, vector2)

    # Calculate the dot product of the two vectors to get the cosine of the angle
    cos_theta = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))

    # Calculate the signed angle in radians using the arctan2 function
    theta = np.arctan2(np.linalg.norm(rotation_axis), cos_theta)
    angle = np.degrees(theta) * np.sign(np.dot(centerPoint, np.cross(vector1, vector2)))
    


    # Calculate the rotation matrix using the Rodrigues formula
    k = rotation_axis / np.linalg.norm(rotation_axis)
    K = np.array([[0, -k[2], k[1]],
                [k[2], 0, -k[0]],
                [-k[1], k[0], 0]])
    rotation_matrix = np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * np.dot(K, K)

    return angle, rotation_matrix

# get crossingpoint of mesh
def get_all_crossingpoints(mesh,ray_origins,ray_directions):
    
    locations, index_ray, index_tri = mesh.ray.intersects_location(ray_origins, ray_directions, multiple_hits=True)
    
    return locations, index_ray, index_tri
