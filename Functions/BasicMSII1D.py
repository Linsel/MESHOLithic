import os,sys

currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 


import numpy as np
import networkx as nx


def get_longest_outline(graph,origin,target):
    outline_list = list(nx.all_simple_paths (graph,origin, target))
    return outline_list[len(outline_list)-1]

def test_nodes_two_neigh(node,neigh_list):
    if len(neigh_list) > 2:
        print('{0} has more than two neighbors.'.format(node))

# # MSII parameter
# def angle_neighbours(newPoint,centerPoint,oldPoint):

#     # Calculate the two vectors from centerPoint
#     vector1 = newPoint - centerPoint
#     vector2 = oldPoint - centerPoint

#     # Calculate the cross product of the two vectors to get the rotation axis
#     rotation_axis = np.cross(vector1, vector2)

#     # Calculate the dot product of the two vectors to get the cosine of the angle
#     theta = np.arccos(np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2)))

#     angle = np.degrees(theta) * np.sign(np.dot(centerPoint, rotation_axis))

#     # theta = np.arctan2(np.linalg.norm(rotation_axis), np.dot(vector1, vector2))
#     # angle = np.degrees(theta) * np.sign(np.dot(centerPoint, np.cross(vector1, vector2)))

#     # Calculate the rotation matrix using the Rodrigues formula
#     k = rotation_axis / np.linalg.norm(rotation_axis)
#     K = np.array([[0, -k[2], k[1]],
#                 [k[2], 0, -k[0]],
#                 [-k[1], k[0], 0]])
#     rotation_matrix = np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * np.dot(K, K)

#     return angle, rotation_matrix    


# MSII parameter
def angle_between_vectors(newPoint,centerPoint,oldPoint):

    # Calculate the two vectors from centerPoint
    vector1 = newPoint - centerPoint
    vector2 = oldPoint - centerPoint

    # Calculate the cross product of the two vectors to get the rotation axis
    rotation_axis = np.cross(vector1, vector2)

    # Calculate the dot product of the two vectors to get the cosine of the angle
    theta = np.arccos(np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2)))

    angle = np.degrees(theta) * np.sign(np.dot(centerPoint, rotation_axis))

    # theta = np.arctan2(np.linalg.norm(rotation_axis), np.dot(vector1, vector2))
    # angle = np.degrees(theta) * np.sign(np.dot(centerPoint, np.cross(vector1, vector2)))

    # Calculate the rotation matrix using the Rodrigues formula
    k = rotation_axis / np.linalg.norm(rotation_axis)
    K = np.array([[0, -k[2], k[1]],
                [k[2], 0, -k[0]],
                [-k[1], k[0], 0]])
    rotation_matrix = np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * np.dot(K, K)

    return angle, rotation_matrix    
