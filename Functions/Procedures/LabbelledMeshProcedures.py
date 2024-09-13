import os,sys

currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

pparentdir = os.path.dirname(parentdir)
sys.path.insert(0, pparentdir) 

from util import *

# compare two operational sequences 
from Functions.EvaluateGraph import directed_edges_parameters

from Functions.EssentialEdgesFunctions import get_manual_edges

# import timing function decorator  
from Functions.EssentialDecorators import timing

from minions.MeshMinions import update_vertex_label#,update_vertex_quality


@timing
def update_label_procedure (obj,**kwargs):

    """         
    
    """


    path = kwargs['path']
    id = kwargs['id']
    preprocessed = kwargs['preprocessed']
    labelfilepath = kwargs['labelfilepath']
    # dict_label = obj.dict_label
    vertices = obj.vertices 
    faces = obj.faces

    obj.load_labelled_mesh(path,id,preprocessed,labelfilepath)

    dict_label = obj.dict_label 

    new_label = np.array([dict_label[n] for n,_ in enumerate(dict_label.items())])

    file_path = ''.join([labelfilepath [:-4],'.ply'])


    # tri_mesh = trimesh.load(''.join([path, id, preprocessed, '.ply']))

    update_vertex_label(vertices,faces,new_label.astype(np.int32),file_path)


@timing
def ridge_prepare_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelfilepath = kwargs ['labelfilepath']


    # Data import and data preparation 
    obj.load_labelled_mesh (path, id, preprocessed, labelfilepath)

    obj.extract_ridges()
    
    obj.prep_ridges()

@timing
def kmeans_label_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelfilepath = kwargs ['labelfilepath']

    obj.load_labelled_mesh(path,id,preprocessed,labelfilepath)

    obj.get_front_and_back_kmeans()

    obj.export_kmeans_labels ()

@timing
def kmeans_slice_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelfilepath = kwargs ['labelfilepath']

    obj.load_labelled_mesh(path,id,preprocessed,labelfilepath)

    obj.get_front_and_back_kmeans()

    obj.kmeans_slice()

@timing
def label_slice_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelfilepath = kwargs ['labelfilepath']

    obj.load_labelled_mesh(path,id,preprocessed,labelfilepath) 

    obj.get_label_submeshes()

    obj.extract_ridges()

    # create node coordinates
    obj.get_centroids()
    # obj.get_NNs()

@timing
def centroids_NNs_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelfilepath = kwargs ['labelfilepath']

    obj.load_labelled_mesh(path,id,preprocessed,labelfilepath) 

    obj.extract_ridges()

    # create node coordinates
    obj.get_centroids()
    obj.get_NNs_ids()

@timing
def direct_graph_area_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelfilepath = kwargs ['labelfilepath']

    obj.load_labelled_mesh(path,id,preprocessed,labelfilepath) 

    obj.get_label_submeshes()    

    edges = get_manual_edges(path, id)

    obj.area = {n:label[0].area for n,label in obj.submeshes.items()}

    directed_edges_parameters(path,id,edges,obj.area,'area')

@timing
def export_ridges_mesh_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelfilepath = kwargs ['labelfilepath']
    
    obj.load_labelled_mesh(path,id,preprocessed,labelfilepath)

    obj.extract_ridges()

    obj.create_ridges_mesh()  

    obj.ridges_mesh.export(''.join ([obj.path, 
                                    obj.id,
                                    '_ridges', 
                                    '.ply']),
                                    file_type='ply')



