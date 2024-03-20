import os,sys

currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
gparentdir = os.path.dirname(parentdir)

prototypedir = '/'.join([gparentdir,'prototyping']) 
minionsdir = '/'.join([gparentdir,'minions']) 

sys.path.insert(0, gparentdir) 
sys.path.insert(0, prototypedir) 
sys.path.insert(0, minionsdir) 

from prototyping.util import *
from prototyping.Classes.BasicClasses import Pline

from scipy.spatial import distance

class Paths (Pline):
    
    def __init__( self,
                path: str = None,
                id: str = None,
                preprocessed: str = None,
                exp_path: str = None,
                tri_mesh: trimesh.Trimesh = None,
                selected_edges: dict = None) -> object:

        """
        A Mesh object contains a triangular 3D mesh.

        Args:
            path (str): String representing the path to the file.
            id (str): String representing the file id of the ply file.
            preprocessed (str): String representing the preprocessing stage of the ply file.
            exp_path (str): String representing the export folder where to save all derived data.
            mesh (trimesh.Trimesh): Trimesh.Trimesh object. 
            selected_vertices (dict): dictionary containing edge label (key) e.g. node ids in graph, and selection of vertex ids (value).
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
        if tri_mesh is not None:
            self.tri_mesh = tri_mesh
        if selected_edges is not None:
            self.selected_edges = selected_edges      


    def shortest_paths(self):

        """
        Finds the shortest path between the preselected edges containing vertices on a triangular 3D mesh.

        Args:
            path (str): String representing the path to the file.
            id (str): String representing the file id of the ply file.
            preprocessed (str): String representing the preprocessing stage of the ply file.
            exp_path (str): String representing the export folder where to save all derived data.
            mesh (trimesh.Trimesh): Trimesh.Trimesh object. 
            selected_vertices (dict): dictionary containing edge label (key) e.g. node ids in graph, and selection of vertex ids (value).


        """        

        # edges without duplication
        edges = self.tri_mesh.edges_unique

        # the actual length of each unique edge
        length = self.tri_mesh.edges_unique_length

        # create the graph with edge attributes for length
        g = nx.Graph()
        for edge, L in zip(edges, length):
            g.add_edge(*edge, length=L)

        shortest_paths = {}
        # run the shortest path query using length for edge weight

        shortest_paths = {label:nx.shortest_path( g,
                                                            source=vertices[0],
                                                            target=vertices[1],
                                                            weight='length') 
                                for label,vertices in self.selected_edges.items()}
        
        shortest_paths_dist = {}
        
        # run the shortest path query using length for edge weight
        for key,ids in shortest_paths.items():
    
            shortest_paths_dist [key] = np.sum([distance.euclidean(self.tri_mesh.vertices[ids[n]],self.tri_mesh.vertices[ids[n+1]]) for n in range(len(ids)-1)])


        # for source,target in self.selected_edges:

        #     shortest_paths[(source,target)] = nx.shortest_path(g,
        #                         source=source,
        #                         target=target,
        #                         weight='length')
            
        self.shortest_paths = shortest_paths

        self.shortest_paths_dist = shortest_paths_dist

    def create_edges_submeshes (self,dict_label):

        self.dict_label = dict_label

        self.edges_submeshes = edges_submeshes (self.tri_mesh,self.dict_label,self.selected_edges)
