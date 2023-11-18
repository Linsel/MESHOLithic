import numpy as np
# from trimesh.curvature import sphere_ball_intersection

import trimesh
import matplotlib.pyplot as plt

def plot_trimesh(mesh):
    # Create a figure and axis object
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Extract the vertices and faces from the mesh object
    vertices = mesh.vertices
    faces = mesh.faces

    # Plot the mesh
    ax.plot_trisurf(vertices[:,0], vertices[:,1], vertices[:,2], triangles=faces, shade=True)

    # Set the axis limits and labels
    ax.set_xlim([vertices[:,0].min(), vertices[:,0].max()])
    ax.set_ylim([vertices[:,1].min(), vertices[:,1].max()])
    ax.set_zlim([vertices[:,2].min(), vertices[:,2].max()])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # Show the plot
    plt.show()

# def create_icospheres(radii):
    
#     icospheres = np.array([trimesh.creation.icosphere(radius=r) for r in radii])  
#     return icospheres

def crossingpoint(origin,target,ico):
       
    crossingdata = get_crossingpoints(ico,[origin],[target])    

    try:
        if not crossingdata[0]:   
            crossingpoint = [0,0,0]
    except:
        crossingpoint = crossingdata[0][0] # get_crossingpoints(ico,[origin],[target])[0][0]
    
    return crossingpoint

def crossingpoints(vertices_dict,edges,ico):

    crossingpoints = {}
    n = 0
    for edge in edges:

        crossingdata = get_crossingpoints(ico,[list(vertices_dict[edge[0]])],[list(vertices_dict[edge[1]])])    
        print(crossingdata)
        try:
            if not crossingdata[0]: 
                pass  
        except:
            n += 1
            crossingpoints[n] = {'origin':edge[0],'target':edge[1],'crossingpoint':crossingdata[0][0]} 
    return crossingpoints

def get_crossingpoints(mesh,origin,target): 
    # Find the intersection of the ray with the mesh
    locations, index_ray, index_tri = mesh.ray.intersects_location(ray_origins=origin, ray_directions=target)

    return locations, index_ray, index_tri

def get_all_crossingpoints(mesh,ray_origins,ray_directions):
    
    locations, index_ray, index_tri = mesh.ray.intersects_location(ray_origins, ray_directions, multiple_hits=True)
    
    return locations, index_ray, index_tri

###########################

from scipy.spatial.distance import pdist, squareform
from scipy.spatial import distance_matrix
from scipy.spatial import distance 

def calc_items_matrix (p_keys):

    link_matrix = np.zeros((len(p_keys), len(p_keys)))

    for n in range(len(p_keys)):
        p_arange = np.arange(n+1,len(p_keys))

        link_matrix[n, n+1:] = p_arange
        link_matrix[n+1:, n] = p_arange
        
    return link_matrix

def calc_polyine_euclidean_distance(p_points):
    """
    Calculates the Euclidean distance matrix of a point cloud of 10 points in an np.array.

    Args:
    points (np.array): The point cloud represented as a numpy array of shape (10, 3).

    Returns:
    np.array: The Euclidean distance matrix represented as a numpy array of shape (10, 10).
    """

    # Calculate the pairwise Euclidean distances between points
    distances = pdist(p_points)

    # Convert the condensed distance matrix to a full distance matrix
    distance_matrix = squareform(distances)
    print('distance_matrix')
    del distances

    return distance_matrix

def find_nearestpoint_outside_range(outline,link_matrix,distance_matrix,II_radius):

    # Find the elementwise points outside the selected distance
    outside_points = np.where(distance_matrix > II_radius)
    print(outside_points)
    del distance_matrix

    # Convert the indices to pairs of items
    outside_pairs = [(outline[i], outline[j]) for i, j in zip(outside_points[0], outside_points[1])]

    print(outside_pairs)

    del outside_points

    # Find the closest item for each elementwise point
    closest_items = [min(outline, key=lambda x: link_matrix[outline.index(x), outline.index(point)]) for point in outside_pairs]

    del outline

    print("Pairs of items outside the selected distance:")
    print(outside_pairs)
    print("Closest item for each pair:")
    print(closest_items)

    # return closest_items  

def find_crossingpoint(polyline,radii):

    p_keys = list(polyline.keys())
    p_points = np.array(list(polyline.values()))
    link_matrix = calc_items_matrix (p_keys)

    distance_matrix = calc_polyine_euclidean_distance(p_points)
    del p_points
    for rad in radii:
        print(rad)
        find_nearestpoint_outside_range(p_keys,link_matrix,distance_matrix,rad)



###########################

from scipy.spatial.distance import pdist, squareform
from scipy.spatial import distance_matrix
from scipy.spatial import distance 


def calc_ecograph_euclidean_distance(vertices,origin,p_points):
    """
    Calculates the Euclidean distance between one origin and a polyline of points.

    Args:
    points (np.array): The point cloud represented as a numpy array of shape (n, 3).

    Returns:
    np.array: The Euclidean distance represented as a dictionary with point:distance 
    as the key:value pair.
    """
    distances = {}

    # Calculate the pairwise Euclidean distances between points
    for p in p_points:
        distances[p] = distance.euclidean(vertices[origin],vertices[p])

    return distances