import os, sys

currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 


import numpy as np
import matplotlib.pyplot as plt
import itertools
import networkx as nx
import trimesh
from plyfile import PlyData,PlyElement


from minions.MeshTxtMinions import write_labels_file

from scipy.spatial import Delaunay

from minions.PathMinions import create_mesh_from_polyline
from scipy.spatial import distance
from minions.DataMinions import create_svg_paths_to_labeled_path,extract_coordinates_from_svg



from IntegralInvariants.II1DClasses import MSIIPline

def arr_to_tuple(arr):

    return tuple(map(tuple, arr))

class testMesh ():

    def __init__(self) -> None:

        self.G = nx.Graph()
        
        self.start_vertices = np.array(((-1.0,-1.0,0.0),(0.0,-1.0,0.0),(1.0,-1.0,0.0),
                                        (1.0,0.0,0.0),(1.0,1.0,0.0), (0.0,1.0,0.0),
                                        (-1.0,1.0,0.0),(-1.0,0.0,0.0)))
        
        # adding upscaled vertices
        self.vertices = np.concatenate ((self.start_vertices,self.start_vertices * 2))
        
        # adding downscaled vertices
        self.vertices = np.concatenate ((self.vertices,self.start_vertices * 0.5))

        # self.start_edges = np.array(((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 0))) 

        # self.edges = np.concatenate ((self.start_edges,self.start_edges + 8))

        # self.edges = np.concatenate ((self.edges,self.start_edges + 16)) 

        # for k,v in enumerate(self.vertices):
        #     self.G.add_node(k,pos=v)

        # for edge in self.edges:
        #     self.G.add_edge(edge[0],edge[1])

        # for n,edge in enumerate(self.edges):

        #     if n == 8:
        #         break

        #     self.G.add_edge(edge[0],edge[0]+8)
        #     self.G.add_edge(edge[0]+9,edge[0])
            
        #     self.G.add_edge(edge[0],edge[0] + 15)
        #     self.G.add_edge(edge[0] + 16,edge[0])

        # for edge in ((17,19),(19,21),(21,23),(23,17),(23,19)):
        #     self.G.add_edge(edge[0],edge[1]) 

        # self.create_3clique_list()
        self.exp_faces = Delaunay(self.vertices [:,:2]).simplices

        self.label = [int((n) / 8) + 1 for n,_ in enumerate(self.vertices)]

    def export_dict(self):

        self.dict = dict(enumerate(self.label))

        write_labels_txt_file (self.dict,self.path + self.id + '_label') 

    def create_3clique_list(self):

        cliques = list(nx.find_cliques(self.G))

        cliques3 = set(sum([list(itertools.combinations(set(clq), 3)) for clq in cliques if len(clq)>=3],[]))
            
        clique3_list = ([list(clique) for clique in cliques3])
            
        self.clique3_list = clique3_list

        self.exp_faces = self.clique3_list
    
    def plot_mesh(self):   
    
        self.pos_2d = {key:vertex[:2] for key,vertex in enumerate(self.vertices)}
        
        nx.draw(self.G,self.pos_2d)     

    def export_testmesh(self,ending,args=None):

        Tuple_List = (('x', 'f4'), ('y', 'f4'), ('z', 'f4'))#,('quality', 'f4'))#, ('label', 'uint8'))

        variable_list = {'x':0,'y':1,'z':2}

        vertices_data_types = dict((i, j) for i, j in Tuple_List)

        exp = np.column_stack([self.vertices])#,quality

        # define 3D point cloud data
        n = exp.shape[0]

        # connect the proper data structures

        vertices = np.empty(n, dtype=list(Tuple_List))

        for i in variable_list:

            vertices[i] = exp[:,variable_list[i]].astype(vertices_data_types[i])

        faces_array = np.empty(len(self.exp_faces), dtype=[('vertex_indices', 'i4', (3,))])
        faces_array['vertex_indices'] = self.exp_faces
        el_faces = PlyElement.describe(faces_array, 'face')
        el_verts = PlyElement.describe(vertices, 'vertex')


        # # save as ply
        ply_data = PlyData([el_verts, el_faces])
        ply_filename_out = "{}{}{}.ply".format(self.path,self.id,ending)
        ply_data.write(ply_filename_out)

class testPolyline ():

    def __init__(self,path,id):

        self.path,self.id  = path,id 

        self.create_basic_info()

        self.G = nx.Graph()

        self.nodes = {0:(1,1,1),1:(2,1,1),2:(3,2,1),3:(2,2,1),4:(3,3,1),5:(1,3,1)}  
        
        self.edges = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,0)]

        for k,v in self.nodes.items():

            self.G.add_node(k,pos=v)

        for edge in self.edges:
            self.G.add_edge(edge[0],edge[1])         

    def add_attributes_nodes(self,attr,attr_name):
        nx.set_node_attributes(self.G, attr, attr_name)
        nx.set_node_attributes(self.DiG, attr, attr_name)        

    def create_basic_info(self):
        self.id = 'testpolyline'
        self.vertices = 6
        self.faces = 0
        self.polylines = 1

        self.dict_mesh_info =   {
                            'Mesh' :    self.id,
                            'Vertices': self.vertices,
                            'Faces' :   self.faces,
                            'Polylines':self.polylines
                            }

    def create_pline(self):

        self.pline = MSIIPline()

        self.pline.polygraphs = {1:{'G':self.G}}

        self.pline.vertices = np.array([ list(self.G.nodes[node]['pos']) 
                                for node in self.G.nodes])

        self.pline.nodes = self.G.nodes

        self.pline.path, self.pline.id  = self.path,self.id 
        
        self.pline.dict_mesh_info = self.dict_mesh_info

        return self

    def plot_polyline_simple(self):

        self.pos_2d = {key:tuple(list(values + np.array([1,-1,0]) )[:2] ) for key,values in self.nodes.items()}

        nx.draw(self.G,self.pos_2d, with_labels = True)

    def plot_polyline_attribute(self,attr):

        self.pos_2d = {key:tuple(list(values)[:2]) for key,values in self.nodes.items()}

        labels = nx.get_node_attributes(self.G,attr)

        nx.draw(self.G,self.pos_2d, labels=labels)        

class testTriangle ():

    def __init__(self) -> None:

        self.G = nx.Graph()

        self.nodes = {0:(1.5,1,1),1:(2,1,1),2:(2,1.5,1)}  
        
        self.edges = [(0,1),(1,2),(2,0)]

        for k,v in self.nodes.items():

            self.G.add_node(k,pos=v)

        for edge in self.edges:
            self.G.add_edge(edge[0],edge[1])

    def plot_polyline(self):

        self.pos_2d = {key:tuple(list(values)[:2]) for key,values in self.nodes.items()}

        nx.draw(self.G,self.pos_2d, with_labels = True)

class testPolylineScaled ():

    def __init__(self,path,id,scales):    

        self.path,self.id = path,id         

        testpolyline = testPolyline()

        self.testpolylines = {scale:self.create_graph(testpolyline.nodes, testpolyline.edges, scale) 
                              for scale in scales}

    def create_graph(self, nodes, edges, scale):

        G = nx.Graph()

        for k,val in nodes.items():

            G.add_node(k,pos=(v * scale for v in val))

        for edge in edges:
            G.add_edge(edge[0],edge[1])    

        return G
    
    def plot_polylines(self,scale):

        temp_polyline = self.testpolylines [scale]

        pos_2d = {key:list(node)[:2] for key,node in temp_polyline.nodes("pos")}

        nx.draw(temp_polyline,pos_2d)   

class testPolylineScaledZ ():

    def __init__(self,path,id,multi_scales,unit):    

        self.path,self.id = path,id   

        testpolyline = testPolyline(path,id)

        self.testpolylines = {n:self.create_digraph(testpolyline.nodes, testpolyline.edges, scales,unit) 
                              for n,scales in enumerate(multi_scales)}
        

    def create_digraph(self, nodes, edges, scales, unit):

        DiG = nx.DiGraph()

        for k,val in nodes.items():
            
            print(tuple(list(val[:2]) + [val[2] * scales[k] / 180 * unit]))

            DiG.add_node(k,pos=(tuple(list(val[:2]) + [val[2] * scales[k] / 180 * unit])))

        for edge in edges:
            DiG.add_edge(edge[0],edge[1])    

        return DiG
    
    def plot_polylines(self,scale):

        temp_polyline = self.testpolylines [scale]

        pos_2d = {key:list(node)[:2] for key,node in temp_polyline.nodes("pos")}

        nx.draw(temp_polyline,pos_2d)   

class testCube ():

    def __init__ (self):

        # create a box with dimensions 1x1x1
        self.box = trimesh.creation.box((1, 1, 1))

        # specify the number of vertices you want
        max_edge = 0.25

        self.sub_box = trimesh.Trimesh()

        # subdivide the box into the specified number of vertices
        self.sub_box.vertices, self.sub_box.faces = trimesh.remesh.subdivide_to_size(self.box.vertices,self.box.faces,max_edge = max_edge)

    def plot_cube(self):

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_trisurf(self.sub_box.vertices[:, 0], self.sub_box.vertices[:,1], triangles=self.sub_box.faces, Z=self.sub_box.vertices[:,2]) 

def testProfileMeshFromSVG (filepath,id,edge):    

        labeled_path = create_svg_paths_to_labeled_path (filepath,id)
        vertices,dict_label = extract_coordinates_from_svg(labeled_path)
        path_dist = sum([distance.euclidean (vertices[i],vertices[i+1]) for i in range(len(vertices)-1)])

        path = {'path': [n for n,_ in enumerate (vertices)], 
                'dist': path_dist}


        create_mesh_from_polyline(filepath,id,edge,path,vertices,dict_label)
    

class testObjects():
    def __init__(self):
        pass

    def preparing(self,path,id):

        self.path = path
        self.id = id

    def create_testpolyline(self):

        self.testpolyline = testPolyline (self.path,self.id)
            
    def create_testProfileMeshFromSVG(self,edge):

        testProfileMeshFromSVG(self.path,self.id,edge)

    def create_testmesh_labeled(self):

        self.testmesh = testMesh ()
     
    def create_testpolyline_scaled(self,scales):       

        self.testpolyline_scaled = testPolylineScaled (self.path,self.id,scales)

    def create_testpolyline_scaled_z(self,scales,unit):       

        self.testpolyline_scaled_z = testPolylineScaledZ (self.path,self.id,scales,unit)

    def create_testcube(self):       

        self.testcube = testCube ()

    def create_testtriangle(self):
        
        self.testtriangle = testTriangle () 
