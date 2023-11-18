import os,sys

currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from util import *

# compare two operational sequences 
from Functions.EvaluateGraph import directededges_parameters

from Functions.EssentialEdgesFunctions import get_manual_edges

# import timing function decorator  
from Functions.EssentialDecorators import timing

@timing
def ridge_prepare_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelname = kwargs ['labelname']
    exp_path = kwargs ['exp_path'] 

    # Data import and data preparation 
    obj.load_labelled_mesh (path, id, preprocessed, labelname, exp_path)

    obj.extract_ridges()
    
    obj.prep_ridges()


@timing
def kmeans_label_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelname = kwargs ['labelname']
    exp_path = kwargs ['exp_path'] 


    obj.load_labelled_mesh(path,id,preprocessed,labelname,exp_path)

    obj.get_front_and_back_kmeans()

    obj.export_kmeans_labels ()

@timing
def kmeans_slice_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelname = kwargs ['labelname']
    exp_path = kwargs ['exp_path'] 


    obj.load_labelled_mesh(path,id,preprocessed,labelname,exp_path)

    obj.get_front_and_back_kmeans()

    obj.kmeans_slice()

@timing
def label_slice_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelname = kwargs ['labelname']
    exp_path = kwargs ['exp_path'] 

    obj.load_labelled_mesh(path,id,preprocessed,labelname,exp_path) 

    obj.get_label_submeshes()

    obj.extract_ridges()

    # create node coordinates
    obj.get_centroids()
    # obj.get_NNs()

@timing
def direct_graph_area_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelname = kwargs ['labelname']
    exp_path = kwargs ['exp_path'] 

    obj.load_labelled_mesh(path,id,preprocessed,labelname,exp_path) 

    obj.get_label_submeshes()    

    edges = get_manual_edges(path, id)

    obj.area = {n:label[0].area for n,label in obj.submeshes.items()}

    directededges_parameters(path,id,edges,obj.area,'area')


@timing
def export_ridges_mesh_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelname = kwargs ['labelname']
    exp_path = kwargs ['exp_path']    
    
    obj.load_labelled_mesh(path,id,preprocessed,labelname,exp_path)

    obj.extract_ridges()

    obj.create_ridges_mesh()  

    obj.ridges_mesh.export(''.join ([obj.path, 
                                    obj.id,
                                    '_ridges', 
                                    '.ply']),
                                    file_type='ply')


@timing
def direct_graph_area_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelname = kwargs ['labelname']
    exp_path = kwargs ['exp_path'] 

    obj.load_labelled_mesh(path,id,preprocessed,labelname,exp_path) 

    obj.get_label_submeshes()    

    edges = get_manual_edges(path, id)

    obj.area = {n:label[0].area for n,label in obj.submeshes.items()}

    directededges_parameters(path,id,edges,obj.area,'area')