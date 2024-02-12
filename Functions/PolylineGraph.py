from util import *

# import numpy as np
import networkx as nx

from skspatial.objects import Line, Sphere
from skspatial.plotting import plot_3d

def create_start_list(p_list,pos_iter):
    
    # using % operator and loop
    # cyclic iteration in list
    
    p_res = []
    for i in range(len(p_list)):
        p_res.append(p_list[pos_iter % len(p_list)])
        pos_iter = pos_iter + 1
    
    return p_res

#create one graphmodel of the polyline
def create_polyline (ordered_nodes):
    
    # create an empty graph
    G = nx.Graph()

    # add nodes to the graph in the desired order
    for i in range(len(ordered_nodes)):
        G.add_node(ordered_nodes[i])

    # adding edges between adjacent nodes
    for i in range(len(ordered_nodes)-1):

        G.add_edge(ordered_nodes[i], ordered_nodes[i+1])

    return G

#create one graphmodel of the polyline
def create_unordered_graph (unordered_nodes):
    
    # create an empty graph
    G = nx.Graph()

    # add nodes to the graph in the desired order
    for i in range(len(unordered_nodes)):
        G.add_node(unordered_nodes[i])

    # adding edges between adjacent nodes
    for i in range(len(unordered_nodes)-1):

        G.add_edge(unordered_nodes[i], unordered_nodes[i+1])

    return G

def get_max_outline(G,origin,target):
    outline_list = list(nx.all_simple_paths (G,origin, target))
    return outline_list

def get_connected_components(G):
    longest_polyline = nx.connected_components(G)
    return longest_polyline

def get_longest_outline(G,origin,target):
    outline_list = list(nx.all_simple_paths (G,origin, target))
    return outline_list[len(outline_list)-1]

# def line_sphere_intersection(line_start, line_dir, sphere_center, sphere_radius):
#     """
#     Determines the intersection point(s) between a line and a sphere in 3D.
    
#     Parameters:
#     line_start (tuple): the starting point of the line (x, y, z).
#     line_dir (tuple): the direction vector of the line (x, y, z).
#     sphere_center (tuple): the center point of the sphere (x, y, z).
#     sphere_radius (float): the radius of the sphere.
    
#     Returns:
#     A tuple containing the intersection point(s) between the line and the sphere, or None if there is no intersection.
#     """
#     # Calculate the coefficients of the quadratic equation
#     a = line_dir[0]**2 + line_dir[1]**2 + line_dir[2]**2
#     b = 2 * (line_start[0]*line_dir[0] + line_start[1]*line_dir[1] + line_start[2]*line_dir[2] - 
#              sphere_center[0]*line_dir[0] - sphere_center[1]*line_dir[1] - sphere_center[2]*line_dir[2])
#     c = line_start[0]**2 + line_start[1]**2 + line_start[2]**2 + sphere_center[0]**2 + sphere_center[1]**2 + sphere_center[2]**2 - 2*(
#         line_start[0]*sphere_center[0] + line_start[1]*sphere_center[1] + line_start[2]*sphere_center[2]) - sphere_radius**2
    
#     # Calculate the discriminant
#     disc = b**2 - 4*a*c
    
#     # If the discriminant is negative, the line and sphere do not intersect
#     if disc < 0:
#         return None
    
#     # Calculate the intersection point(s)
#     t1 = (-b + math.sqrt(disc)) / (2*a)
#     t2 = (-b - math.sqrt(disc)) / (2*a)
#     p1 = (line_start[0] + t1*line_dir[0], line_start[1] + t1*line_dir[1], line_start[2] + t1*line_dir[2])
    
#     # If the discriminant is zero, there is only one intersection point
#     if disc == 0:
#         return p1
    
#     p2 = (line_start[0] + t2*line_dir[0], line_start[1] + t2*line_dir[1], line_start[2] + t2*line_dir[2])

#     p1_d= np.linalg.norm(np.array(line_dir)-np.array(p1)) 
#     p2_d= np.linalg.norm(np.array(line_dir)-np.array(p2)) 

#     if p1_d > p2_d:
#         return p2
#     elif p1_d < p2_d:
#         return p1

def line_sphere_intersection(origin, target, sphere_center, sphere_radius):

    """
    Determines the intersection point point_b between a line and a sphere in 3D.
    
    Parameters:
    origin (tuple): the starting point of the line (x, y, z).
    target (tuple): the direction vector of the line (x, y, z).
    sphere_center (tuple): the center point of the sphere (x, y, z).
    sphere_radius (float): the radius of the sphere.
    
    Returns:
    A np.array containing the intersection point_b between the line and the sphere, or None if there is no intersection.
    """    

    target = np.array(target) - np.array(origin)

    sphere = Sphere(sphere_center, sphere_radius)
    line = Line(origin, target)

    point_a, point_b = sphere.intersect_line(line)

    return np.array(point_b)

def get_cycle(G:nx.graph):

    """
    Finds the largest cycle in an undirected graph and returns it along with its reverse.

    Args:
        G (nx.Graph): A NetworkX graph object.

    Returns:
        tuple: A tuple containing two elements:
            - cycle (list): longest cycle in graph.
            - rev_cycle (list): longest cycle (reversed) in graph.

    """    

    max_cycle = max([len(cycle) for cycle in nx.cycle_basis(G)])

    cycle = [cycle for cycle in nx.cycle_basis(G) if len(cycle) == max_cycle][0]

    cycle = cycle + [cycle[0]]

    rev_cycle = list(reversed(cycle))

    return cycle,rev_cycle
