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

from minions.MeshMinions import quick_plot_mesh
from minions.PathMinions import mesh_transform_two_vertices,align_mesh_principal_component,add_edges_from_faces,increase_path_size,shortest_distance,create_mesh_from_polyline
from Functions.exportFiles.writeTxt import write_labels_txt_file

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
        edges = self.edges_unique

        # the actual length of each unique edge
        length = self.edges_unique_length

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
    
            shortest_paths_dist [key] = np.sum([distance.euclidean(self.vertices[ids[n]],self.vertices[ids[n+1]]) for n in range(len(ids)-1)])


        # for source,target in self.selected_edges:

        #     shortest_paths[(source,target)] = nx.shortest_path(g,
        #                         source=source,
        #                         target=target,
        #                         weight='length')
            
        self.shortest_paths = shortest_paths

        self.shortest_paths_dist = shortest_paths_dist

    def path_profile (self):
        
        tri = self.tri_mesh.copy()

        path_profiles = {}

        for edge_ids, vert_ids in self.selected_edges.items():

            verts = {0:tri.vertices[vert_ids[0]], 
                    1:tri.vertices[vert_ids[1]]}
            
            mesh_transform_two_vertices(tri, verts)

            # align_mesh_principal_component(tri)

            lines,faces = trimesh.intersections.mesh_plane(tri,[0,1,0],[0,0,0],return_faces=True)

            # creates a line graph, which is not sufficient to build a complete cycle graph
            # create_lines_graph ()
            
            face_verts = set()
            G = nx.Graph()
            for face_id in faces:

                face = tri.faces[face_id]

                G = add_edges_from_faces(tri,G,face)

                [face_verts.add (vert) for vert in face]
    

            try:
                shortest_paths = nx.shortest_path(G,
                                                source=vert_ids[0],                                        
                                                target=vert_ids[1],                                        
                                                weight='length')     


                shortest_paths_dist = np.sum([G.edges[(v,int(shortest_paths[n+1]))]['length'] for n,v in enumerate(shortest_paths[:-1])])

            except:
                selected_face_verts = set()
                try:
                    selected_face_verts,selected_faces = increase_path_size (tri,face_verts,selected_face_verts)
                    shortest_paths, shortest_paths_dist = shortest_distance(tri,vert_ids,selected_faces)
                except:
                    try:
                        selected_face_verts,selected_faces = increase_path_size (tri,face_verts,selected_face_verts)
                        shortest_paths, shortest_paths_dist = shortest_distance(tri,vert_ids,selected_faces)
                    except:
                        shortest_paths, shortest_paths_dist = 0,0
                        print(edge_ids)

            path_profiles [edge_ids] =  {'path':shortest_paths,'dist':shortest_paths_dist}
            
        return path_profiles        


    def path_turned_profile (self):

        tri = self.tri_mesh.copy () 
        
        path_profiles = {}

        for edge_ids, vert_ids in self.selected_edges.items():

            verts = {0:tri.vertices[vert_ids[0]], 
                    1:tri.vertices[vert_ids[1]]}
            

            tri, trafo_mat = mesh_transform_two_vertices(tri, verts)

            submesh = self.edges_submeshes [edge_ids].copy()
            submesh.apply_transform(trafo_mat)

            align_mesh_principal_component(tri,submesh)

            lines,faces = trimesh.intersections.mesh_plane(tri,[0,1,0],[0,0,0],return_faces=True)

            # creates a line graph, which is not sufficient to build a complete cycle graph
            # create_lines_graph ()
            
            face_verts = set()
            G = nx.Graph()
            for face_id in faces:

                face = tri.faces[face_id]

                G = add_edges_from_faces(tri,G,face)

                [face_verts.add (vert) for vert in face]
    

            try:
                shortest_paths = nx.shortest_path(G,
                                                source=vert_ids[0],                                        
                                                target=vert_ids[1],                                        
                                                weight='length')     


                shortest_paths_dist = np.sum([G.edges[(v,int(shortest_paths[n+1]))]['length'] for n,v in enumerate(shortest_paths[:-1])])

            except:
                selected_face_verts = set()
                try:
                    selected_face_verts,selected_faces = increase_path_size (tri,face_verts,selected_face_verts)
                    shortest_paths, shortest_paths_dist = shortest_distance(tri,vert_ids,selected_faces)
                except:
                    try:
                        selected_face_verts,selected_faces = increase_path_size (tri,face_verts,selected_face_verts)
                        shortest_paths, shortest_paths_dist = shortest_distance(tri,vert_ids,selected_faces)
                    except:
                        shortest_paths, shortest_paths_dist = 0,0
                        print(edge_ids)

            shortest_paths_vertices = [tri.vertices[vert] for vert in shortest_paths]                   

            path_profiles [edge_ids] =  {   'path':shortest_paths,
                                            'dist':shortest_paths_dist, 
                                            'vertices':shortest_paths_vertices,
                                            'trafo_mat':trafo_mat}

        return path_profiles


    def generate_mesh_from_polyline(self,
                                    paths:dict):


        """
        Creates from a passed dictionary containing test objects as meshes (.ply). 

        Args:
            paths (dict): dictionary containing edge label (tuple) as key e.g. node ids in graph, and a dictionary containing the keys:
                - path (list): list of vertex ids along the path. 
                - dist (float): distance of the complet path
        """         

        for edge, path in paths.items():

            create_mesh_from_polyline(self.path,self.ind,edge,path,self.tri_mesh.vertices,self.dict_label)

            # # Define the initial polyline as a nested list of coordinates 
            # polyline = [list(self.tri_mesh.vertices[ind]) for ind in path['path']]
            # polyline_labels = [self.dict_label[ind] for ind in path['path']]

            # # Derive parameter like length of polyline in vertices () and the spacing between each profile (z_spacing)
            # PL_len = len([v for v in polyline])
            # z_spacing = path['dist']/PL_len    

            # # create parallel profiles with an offset of z_spacing
            # profiles = [np.array(polyline) + np.array([0, 0, z]) for z in np.linspace(0, z_spacing * (PL_len - 1), PL_len)]
            # profiles_labels = {i: polyline_labels[i % len(polyline_labels)] for i in range(PL_len * len(polyline_labels))} 
            # profiles_verts = [vert for profile in profiles for vert in profile]

            # faces = []
            # # Generate faces based on the provided indexing strategy (right hand rule)
            # for i in range(PL_len - 1):
            #     for j in range(len(polyline) - 1):
            #         triangle1 = [i*PL_len+j+1, i*PL_len+j, (i+1)*PL_len+j]
            #         triangle2 = [(i+1)*PL_len+j+1, i*PL_len+j+1, (i+1)*PL_len+j]
            #         faces.append(triangle1)
            #         faces.append(triangle2)

            # # Creating mesh 
            # mesh = trimesh.Trimesh( vertices=profiles_verts, 
            #                         faces = faces)
            # # Exporting mesh 
            # mesh.export(''.join([self.path,self.id, '-'.join([str(edge[0]),str(edge[1]), 'profile.ply']) ]))

            # write_labels_txt_file(profiles_labels,''.join([self.path,self.id, '-'.join([str(edge[0]),str(edge[1]), 'profile-labels']) ]))

            # # Creating renderings of new mesh 
            # quick_plot_mesh(mesh)

        

    # def create_edges_submeshes (self,dict_label):

    #     self.edges_vertices = find_edges_vertices (edges,labels)

    #     self.edges_submeshes = edges_submeshes (self.tri_mesh,self.dict_label,self.selected_edges)
