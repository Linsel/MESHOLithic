from util import *

def find_vertices_within_radius(mesh: object, 
                                start_vertex: np.ndarray, 
                                radius: float):
    # Compute the distance between start_vertex and all other vertices
    distances, indices = mesh.kdtree.query(start_vertex, k=len(mesh.vertices))
    
    # Filter the indices to include only vertices within the specified radius
    indices_within_radius = indices[distances <= radius]
    
    return indices_within_radius

def metadata_label_array(   metadata: np.ndarray,
                            labels: dict) -> np.ndarray:

    """
    Converts the metadata dictionary of a trimesh mesh object to a structured array and 
    adds a labelid column.

    Args:
        metadata (ndarray): Metadata of a trimesh mesh object
        labels (dict): vertex:label dictionary of the trimesh mesh object

    Returns:
        ndarray: The structured array representing the metadata of the .
    """
    
    names = [key for key in metadata ['vertex']['properties'].keys()]
    formats = [val for val in metadata ['vertex']['properties'].values()]

    num = [n for n,key in enumerate(metadata ['vertex']['properties']) 
                if key == 'labelid'][0]

    formats[num] = '<U10'

    data = metadata ['vertex']['data']

    dtype = dict(names = names, formats=formats)

    metadata_arr = np.array(data, dtype=dtype)

    metadata_arr ['labelid'] = [labels[str(n)] for n,_ in enumerate(metadata)]

    return metadata_arr

def get_nearest_neighbor(   mesh: object,
                            point: np.ndarray) -> np.ndarray:

    """
    Function to get nearest vertex of the point of the mesh surface 

    Args:
        mesh (trimesh.mesh): trimesh mesh object 
        point (np.ndarray (3,)): coordinates of the point in 3D 

    Returns:
        NN (np.ndarray (3,)): coordinates of the nearest neighbour (NN) in 3D 

        
    """        

    # Build a KD-tree from the vertices
    kdtree = mesh.kdtree
        
    # Query the kdtree for the nearest neighbor from the query point and get distance to NN + index of NN
    dist, index = kdtree.query(point)

    # Get nearest neighbor as coordinates
    NN = mesh.vertices[index]

    return NN

def create_label_submeshes (mesh,labels):

    """
    Creates submeshes of mesh according to passed labels. 
    
    Args:
        mesh (trimesh object): trimesh mesh object
        labels (dict): A dictionary containing unique_labels (keys) and vertex ID's (values).             

    Returns: 
        submeshes (dict): A dictionary of submeshes of the original labelled mesh.

    """    
    
    selected_faces =   {   label:
                                    np.all(np.isin(mesh.faces,values), axis=1)
                                for label,values in labels.items()
                            }

    submeshes = {   label:
                            mesh.submesh([selected_faces[label]])
                        for label in labels.keys()
                    }

    return submeshes

def get_submesh_quality (quality, vertlist):

    """
    Returns the quality property of a submesh in the quality dictionary.
    """      

    sub_quality =  {n:quality[n] for n in vertlist}

    return sub_quality

# This function returns the most common element in a list of values.
def most_common_neighbour_label (lst):

    return max(set(lst), key=lst.count)

def convert_to_ply(path,name,ending):

    # Load your STL file
    mesh = trimesh.load(''.join([path,name,ending]))

    # Export as PLY
    try:
        mesh.export(''.join([path,name,'.ply']))
    except: 
        print('{} is empty!'.format(name))