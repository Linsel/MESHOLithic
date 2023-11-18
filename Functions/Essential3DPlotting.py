
from util import *

# import angle between vectors
from Functions.BasicMSII1D import angle_between_vectors
from Classes.Primitive_3D.EdgeShapes3D import generate_unitarrow,generate_unitconnection
from scipy.spatial import distance

## nodes 
def create_node_sphere (origin,radius):
    
    # Create sphere with radius of radius, 642 vertices and 1280 faces
    icosphere = trimesh.creation.icosphere(radius=radius)
    
    # Translation vector to position the arrow body
    icosphere.apply_translation(origin)

    return icosphere   

## arrows
def arrow_trafomat(circumference,node_dist,trafomat):

    arrow_mesh = generate_unitarrow()

    # scale width and depth to according to II1d-difference1 between ridges lines 
    arrow_mesh.vertices[:,0]  = arrow_mesh.vertices[:,0] * circumference 
    arrow_mesh.vertices[:,1]  = arrow_mesh.vertices[:,1] * circumference

    # scale the length to distance between scar reference point
    arrow_mesh.vertices[:,2]  = arrow_mesh.vertices[:,2] * node_dist

    # transforms mesh sccording to imported trafomat
    arrow_mesh.apply_transform(trafomat)
    
    return arrow_mesh

# apply trafomat and scale according to parameters 
def connection_trafomat (circumference,node_dist,trafomat):

    connection_mesh = generate_unitconnection()

    # scales width and depth to according to II1d-difference1 between ridges lines 
    connection_mesh.vertices[:,0]  = connection_mesh.vertices[:,0] * circumference
    connection_mesh.vertices[:,1]  = connection_mesh.vertices[:,1] * circumference

    # scales the length to distance between scar reference point
    connection_mesh.vertices[:,2]  = connection_mesh.vertices[:,2] * node_dist

    # transforms mesh sccording to imported trafomat    
    connection_mesh.apply_transform(trafomat)
        
    return connection_mesh

# unscaled edge width
def create_rotated_arrow (edge,centroids,circumference):

    arrow_transformed = None

    origin, target = centroids [edge[0]], centroids [edge[1]]

    node_dist = distance.euclidean(origin, target)

    _, trafomat = angle_between_vectors (origin + [0,0,node_dist],
                                origin,
                                target)
    
    trafomat = np.vstack((trafomat.T,origin))

    trafomat = np.vstack((trafomat.T,np.array([0,0,0,0])))
    
    arrow_transformed = arrow_trafomat(circumference, node_dist, trafomat)

    return trafomat,arrow_transformed

# scaled edge circumference
def create_rotated_connection (edge,centroids,circumference):

    connection_transformed = None

    origin, target = centroids [edge[0]], centroids [edge[1]]

    scale = distance.euclidean(origin, target)

    _, trafomat = angle_between_vectors(origin + [0,0,scale],
                                        origin,
                                        target)
    
    trafomat = np.vstack((trafomat.T,origin))

    trafomat = np.vstack((trafomat.T,np.array([0,0,0,0])))
    
    connection_transformed = connection_trafomat(circumference, scale, trafomat)

    return trafomat,connection_transformed