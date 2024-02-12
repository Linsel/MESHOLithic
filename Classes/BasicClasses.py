"""

BasicClasses.py
-------------

"""

from util import *

# import timing function decorator  
from Functions.EssentialDecorators import timing

# import functions to evaluate correctness of directed edges  
from Functions.EvaluateGraph import evaluate_directed_edges 

# import functions to alter meshes  
from Functions.EssentialMeshAlteration import find_vertices_within_radius,get_nearest_neighbor

# import functions to export pline file
from Functions.PlineExport import exp_pline, exp_pline_funcvals

# sphere_ball_intersection or gaussian curvature  
from trimesh.curvature import sphere_ball_intersection,discrete_gaussian_curvature_measure

# 
class Mesh:

    """
    The Mesh object is the parent object of many analytical classes, 
    including pointCloud, and labelledMesh objects. Mostly based on
    Trimesh.Trimesh class.
    """


    def __init__( self,
                path: str = None,
                id: str = None,
                preprocessed: str = None,
                exp_path: str = None,
                vertices: np.ndarray = None,
                faces: np.ndarray = None,
                normals: np.ndarray = None,
                metadata: np.ndarray = None,
                edges: np.ndarray = None,
                vertex_neighbors: list = None,
                vertex_attributes: dict = None,
                vertex_adjacency_graph: nx.Graph = None,
                vertex_neighbors_dict: dict = None) -> object:

        """
        A Mesh object contains a triangular 3D mesh.

        Args:
            path (str): String representing the path to the file.
            id (str): String representing the file id of the ply file.
            preprocessed (str): String representing the preprocessing stage of the ply file.
            exp_path (str): String representing the export folder where to save all derived data.
            vertices (ndarray): Array of vertex locations with shape (n, 3).
            faces (ndarray): Array of triangular faces with shape (m, 3).
            normals (ndarray): Array of normal vectors for vertices with shape (n, 3).
            metadata (ndarray): Array of integers representing any metadata about the mesh with shape (n, 2).
            edges (ndarray): List of vertex indices making up edges with shape (n, 2).
            vertex_neighbors (list): List of vertex neighbors.
            vertex_adjacency_graph (nx.Graph): Graph representing vertices and edges between them, where vertices are nodes and edges are edges.
            vertex_neighbors_dict (dict): Dictionary with vertex indices as keys and adjacent neighbors as values.
        """

        # check for None only to avoid warning messages in subclasses
        if path is not None:
            self.path = path
        if id is not None:
            self.id = id
        if preprocessed is not None:
            self.preprocessed = preprocessed
        if exp_path is not None:
            self.exp_path = exp_path
        if vertices is not None:
            self.vertices = vertices
        if faces is not None:
            self.faces = faces
        if normals is not None:
            self.normals = normals
        if metadata is not None:
            self.metadata = metadata
        if edges is not None:
            self.edges = edges
        if vertex_neighbors is not None:
            self.vertex_neighbors = vertex_neighbors
        if vertex_adjacency_graph is not None:
            self.vertex_adjacency_graph = vertex_adjacency_graph
        if vertex_neighbors_dict is not None:
            self.vertex_neighbors_dict = vertex_neighbors_dict            

    @timing
    def load_ply(self, 
                path: str = None,
                id: str = None,
                preprocessed: str = None,
                exp_path: str = ''):

        """
        Function to load a ply file to the Mesh object
        
        Args:
            path (str): String representing the path to the file.
            id (str): String representing the file id of the ply file.
            preprocessed (str): String representing the preprocessing step of the ply file.
            exp_path (str): String representing the export folder where to save all derived data.
        """
        
        # save all attributes 
        self.path = path
        self.id = id     
        self.preprocessed = preprocessed   
        self.exp_path = exp_path

        # create export folder
        if os.path.isdir(path + exp_path) == False:
            os.mkdir(path + exp_path)

        self.tri_mesh = trimesh.load(''.join([path, id, preprocessed, '.ply']))

        # Read the vertex data as array
        self.vertices = np.array(self.tri_mesh.vertices)

        # Read the normals data as array
        self.normals = np.array(self.tri_mesh.vertex_normals)        

        # Read the vertex data as array
        self.vertices_dict = {n:v for n,v in enumerate(self.tri_mesh.vertices)}

        # Read the face data as array
        self.faces = np.array(self.tri_mesh.faces)
        
        # Read the edge data
        self.edges = self.tri_mesh.edges

        # Read a list of vertex_neighbors
        self.vertex_neighbors = self.tri_mesh.vertex_neighbors

        # Read the vertex_adjacency_graph        
        self.vertex_adjacency_graph = self.tri_mesh.vertex_adjacency_graph        

        # Create a dict of vertex_neighbors
        self.vertex_neighbors_dict = {num: vertex_neighbors 
                                           for num, vertex_neighbors in enumerate(self.vertex_neighbors)}
         
    def get_quality(self):

        """
        Saves the quality separately in the quality variable.
        """      

        self.quality = self.tri_mesh.metadata ['ply_raw']['vertex']['data']['quality']

    # saving quality in accesible variable or calculating the maximum gaussian curvature in 8 diffent radii
    def get_or_calc_curvature(self):

        """
        Accesses the quality or calculates the maximum discrete Gaussian curvature in 8 spheres with equidistant radii.
        """          

        try:
            # Read the quality as curvature of vertices
            self.get_quality()
            
        except:
            # radii in which the gaussian curvature gets measured
            radii = np.linspace(0.001, 2.0, 8)
            # Calculate the Gaussian curvature and set it in ratio to the sphere_ball_intersection
            self.quality = np.array([np.max(g) for g in np.array([discrete_gaussian_curvature_measure(self.tri_mesh, self.vertices, r)/sphere_ball_intersection(1, r) for r in radii]).T])

    # def get_vertices(self):
    #     """
    #     Returns coordinates of vertices 
        
    #     Returns
    #     ------------
    #     vertices : (n, 3) float 
    #         Array of vertex locations

    #     """

    #     return self.vertices
    
    # def get_faces(self):
    #     """
    #     Returns coordinates of vertices to convert metadata dictionary to array 
        
    #     Returns
    #     ------------
    #     faces : (m, 3) 
    #         Array of triangular 
    #     """

    #     return self.faces
    
    # def get_edges(self):
    #     """
    #     Returns coordinates of vertices to convert metadata dictionary to array 
        
    #     Returns
    #     ------------
    #     edges : (n, 2) int
    #         List of vertex indices making up edges
    #     """        
    #     return self.edges

    # def get_vertex_neighbors(self):
    #     return self.vertex_neighbors
    
    # def get_vertex_adjacency_graph(self):
    #     return self.vertex_adjacency_graph
    
    # def get_positon_value_metadata(self,columnname):
    #     return self.metadata ['vertex']['properties'][columnname]


    # def command_line_GigaMesh(self, path, id, method, parameters = ' '):

    #     giga_path = "~/Downloads/build-GigaMesh-Desktop_Qt_5_15_2_GCC_64bit-Debug/cli/"

    #     os.chdir(path)
        
    #     os.system("{0}{1}{2}{3}{4}{5}{6}".format(str(giga_path),str(method),' ', str(parameters), ' ' , str(id) ,'.ply'))

#
class Pline:
    """
    The Pline object stores the Pline file generated according to the GigaMesh Software Standard. 
    """

    def __init__(self,
                 path: str = None,
                 id: str = None,
                 dict_mesh_info:dict = None,
                 dict_plines:dict = None):

        """
        A Pline object contains multiple Polylines, which are structured according to the GigaMesh Polyline Standard.

        Args:
            path (str): String representing the path to the file.
            id (str): String representing the file id of the ply file.             
            dict_mesh_info (dict): Any metadata about the mesh.
            dict_plines (dict): Any data of the polylines.
        """
   
        # check for None only to avoid warning messages in subclasses
        if path is not None:
            self.path = path
        if id is not None:
            self.id = id
        if dict_mesh_info is not None:
            self.dict_mesh_info = dict_mesh_info
        if dict_plines is not None:
            self.dict_plines = dict_plines

    @timing
    def from_pline(self, 
                   path: str, 
                   id: str):
    
        """
        Load a pline file to the Pline object.

        Args:
            path (str): The path to the file.
            id (str): The file ID of the _polyline.pline file.

        """

        self.path = path 
        self.id = id
        self.filename = ''.join([self.path, self.id,'_polyline.pline'])


        with open(self.filename, "r") as f:
            data = f.readlines()

        self.store_mesh_information(data)

        self.store_pline_information(data)

    def store_mesh_information(self,
                               data: list):

        """
        Function to extract the metadata of the mesh  
        
        Args:
            data (list): A list of strings containing imported pline data.

        """
        
        for line in data[10:15]:
            line = line [4:].replace('\n','')

            if line [:2] != '- ':
                line_label = line.split(':')
            else:
                line_label = line[2:].split(':')

            line_info = line_label[1].split('  ')

            if line_label[0] == 'Timestamp':
    
                self.dict_mesh_info [line_label[0]] = ' '.join(line_info [len(line_info)-2:]) + ':'.join([''] + line_label[len(line_label)-2:])

            elif line_label[0] == 'Mesh':
                self.dict_mesh_info [line_label[0]] = line_info [len(line_info)-1][1:].replace('"','')

            else:
                self.dict_mesh_info [line_label[0]] = int(line_info [len(line_info)-1])

    def store_pline_information(self,
                                data: list):

        """
        Function to extract the polyline data.

        Args:
            data (list): A list of strings containing imported pline data.

        """

        # store all polyline information
        for n,line in enumerate(data[18:]):
            line = list(map(float, line.split(' '))) 
            
            label_no = int(line[0])

            vertices_no = int(line[1])
            properties = np.dtype([('idx', np.int8), ('x', np.float64), ('y', np.float64),('z', np.float64), ('nx', np.float64), ('ny', np.float64),('nz', np.float64)])
            dtype = np.dtype({'names': ['idx', 'x', 'y', 'z', 'nx', 'ny', 'nz'], 'formats': [np.int8, np.float64, np.float64, np.float64, np.float64, np.float64, np.float64]})
                        
            data = np.array(line[2:]).reshape(int(len(line[2:])/7),7) 
            
            vertices = [int(da[0]) for da in data]

            data = np.array(data[:,1:])

            self.dict_plines[n + 1] = {'label_id':label_no, 'vertices_no':vertices_no, 'vertices':vertices, 'metadata':{'properties':properties, 'data':data}}

        self.vertices = {values['vertices'][n]:values['metadata']['data'][n,:3] for values in self.dict_plines.values() for n,val in enumerate(values['vertices'])}
        self.normals = {values['vertices'][n]:values['metadata']['data'][n,3:] for values in self.dict_plines.values() for n,val in enumerate(values['vertices'])}         

    def export_pline(self):

        """       
        Export of Pline as pline file according to the GigaMesh Polyline Standard.
        """        

        exp_pline(self.path, self.id, self.dict_mesh_info, self.dict_plines, self.vertices, self.normals)


    def export_pline_funcvals(self):
        """       
        Export of Pline function values as txt file according to the GigaMesh Polyline Standard.
        """        

        exp_pline_funcvals(self.path, self.id, self.dict_mesh_info, self.funcvals, self.var_name)

    def create_exp_vertices_normals(vertices: np.ndarray,
                                    normals: np.ndarray,
                                    polyline: dict) -> str:

        """
        Creates a string representation for all vertices (coordinates and normals) belonging to one polyline.

        Args:
            polyline (dict): A dictionary containing all data of a polyline.

        Returns:
            str: The string representation of vertices and normals.

        """

        exp_vertices_normals =  ' '.join(str(vertex) + 
                                ' ' + 
                                ' '.join([str(i) for i in vertices[vertex]]) +
                                ' ' + 
                                ' '.join([str(i) for i in normals[vertex]])
                                
                                for vertex in polyline['vertices'])

        return exp_vertices_normals

class manualEdges:

    """
    The manualEdges object is used to evaluate automatically generated directed graph models.
    """

    def __init__(   self,
                    path: str = None,
                    id: str = None) -> object:

        """
        A manualEdges object contains edges and nodes of a manually conducted chaîne opératoire.

        Import manually created edge data of chaîne opératoire graph model,
        either with identically or with differently named nodes to the gt_label.

        Attributes:
            path (str): String representing the path to the file.
            id (str): String representing the file id of the ply file.

        """

        # check for None only to avoid warning messages in subclasses
        if path is not None:
            self.path = path
        if id is not None:
            self.id = id

    # import manual edges, identically named nodes 
    def import_edges (  self,
                        path: str,
                        id: str):

        """
        Function to load an edge file into a manualEdges object.

        Args:
            path (str): String representing the path to the file.
            id (str): String representing the file id of the _polyline.pline file.

        Attributes:
            manual_edges (set): Set of manually determined edges.
        """

        self.path = path
        self.id = id          

        edge_df = pd.read_csv(''.join([self.path,self.id,'_links','.csv']),
                                sep=',',header=0)

        
        self.manual_edges  = {(int(edge[0]),int(edge[1])) for _,edge in edge_df.iterrows()}

    # import manual edges, differently named nodes, hence also importing and renaming of nodes 
    def import_edges_nodes (self,
                            path: str,
                            id: str):

        """
        Function to load edges and nodes files to manualEdges object
        
        Args:
            path (str): String representing the path to the file.
            id (str): String representing the file id of the _polyline.pline file.

        Attributes:
            manual_nodes (dict): Dictionary of annotated label of node (key) and manual node (value).
            manual_edges (set): Set of manually determined edges.

        """

        self.path = path
        self.id = id          

        nodes_df = pd.read_csv(''.join([self.path,self.id,'_nodes','.csv']),
                                sep=',',header=0)
        


        self.manual_nodes = {node[-1]: {nodes_df.columns[n]:para for n,para in enumerate(node[:-1])} 
                    
                        for _,node in nodes_df.iterrows()
                        }
        
        edge_df = pd.read_csv(''.join([self.path,self.id,'_links','.csv']),
                                sep=',',header=0)
        
        
        self.manual_edges = {(int(nodes_df[nodes_df['node'] == edge['source']]['gt_label']),
                        int(nodes_df[nodes_df['node'] == edge['target']]['gt_label']))
                    
                        for _,edge in edge_df.iterrows()}
        
    # create a DiGraph of the manually generate operational sequence
    def create_manual_DiGraph (self):

        """
        Create a manual directed Graph of manual edges. 
        
        """
        
        self.DiG_manual = nx.DiGraph()

        for edge in self.manual_edges:
            self.DiG_manual.add_nodes_from(edge)
            self.DiG_manual.add_edge(*edge)


    # compare two operational sequences 
    def compare_operational_sequences (self,
                                       edge: set):

        """
        Function to compare the imported manually created edge model with a second edge model, which can include a second manually created edge model or can be derived algorithmically.
        The manual edges are considered to be the groundtruth and the edge_set is  
        

        Args:
            edge (set): A set consisting of directed edge pairs.

        Returns:
            eval_edge_direction (dict): A dictionary of edges, indicating whether they are correctly (1) or incorrectly (0) directed.
            accuracy (float): The accuracy of the edge_set compared to the manual edges.
        """
     
        eval_edge_direction, accuracy = evaluate_directed_edges(edge, self.manual_edges)# n_components = 3

class NpEncoder(json.JSONEncoder):

    """
    The NpEncoder object is used to encode a numpy array for including in .json file.
    """

    def default(self, 
                obj: object):
        """
        Transforms numpy data to Python data types.

        Args:
            obj (object): A numpy object, can be np.integer, np.int64, np.float, or np.ndarray.

        Returns:
            int: Converted to int if obj is np.integer or np.int64.
            float: Converted to float if obj is np.float.
            list: Converted to list if obj is np.ndarray.

        """

        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.int64):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)        
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


# class ridgeGraph:

#     """
#     The ridgeGraph object is used to create a undirected Graph model of ridges.
#     """

#     def __init__(self) -> None:

#         """
#         A ridgeGraph object contains edges and nodes of an undirect ridge Graph model. 

#         """


#         pass

#     # preprocessing 
#     def prep_ridges(self):
      

#         self.dict_ridge_notshared_label = {val: {self.dict_label[v] for v in self.vertex_neighbors_dict[val] 
#                                                 if self.dict_label[val] != self.dict_label[v] and 
#                                                 self.dict_label[v] not in self.no_polyline}
                                                
                                        
#                                                 for key, vals in self.label_outline_vertices.items()
#                                                 for val in vals
#                                                 }                                                



#         self.set_neighbouring_labels = {(key,self.dict_label[v])
                                
#                                                 for key, vals in self.label_outline_vertices.items()
#                                                 for val in vals
#                                                 for val in vals for v in self.vertex_neighbors_dict[val] # + [self.dict_label[val]] 
#                                                         if self.dict_label[val] != self.dict_label[v]
#                                         }
#         # dictionary with 
#         self.neighbouring_labels = {u_l:[{v1 for v1,v2 in self.set_neighbouring_labels if v2 == u_l} | {v2 for v1,v2 in self.set_neighbouring_labels if v1 == u_l}][0]  
                                
#                                                 for u_l in self.label_outline_vertices.keys() 
                                                
#                                         }       

#     def plot_ridegraph(self,attr):
#         pos=nx.spring_layout(self.G_ridges)
#         nx.draw(self.G_ridges)
#         labels = nx.get_edge_attributes(self.G_ridges,attr)
#         nx.draw_networkx_edge_labels(self.G_ridges,pos,edge_labels=labels)

#     def create_manual_edges(self):

#         self.manualEdges = manualEdges(self.path,self.id)

#     def get_basic_graph_properties(self,graph):

#         dict_degree = dict(graph.degree)

#         dict_degree_weigthed = dict(graph.degree(weight='weight'))    

#         dict_betweenness_centrality = nx.betweenness_centrality(graph, endpoints=True,normalized=True)


#         properties = {edge:{'degree':dict_degree[edge], 
#                             'degree_weigthed':dict_degree_weigthed[edge], 
#                             'betweenness_centrality' : dict_betweenness_centrality[edge]} 
#                                 for edge in dict_degree.keys()}
        
#         return properties
    
