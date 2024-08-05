import json
import trimesh
import pandas as pd

from Functions.EssentialMeshAlteration import create_label_submeshes
from Functions.EssentialLabelAlteration import get_uniquelabel_vertlist


def submeshes_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelfilepath = kwargs ['labelfilepath']


    obj.load_labelled_mesh(path,id,preprocessed,labelfilepath) 

    obj.get_quality()

    obj.get_label_submeshes()    
    
    return obj

def submeshes_mean_quality_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelfilepath = kwargs ['labelfilepath']

    del kwargs

    print('step:',1)
    obj.load_labelled_mesh(path,id,preprocessed,labelfilepath) 

    obj.get_quality()
    print('step:',2)
    submesh_properties = {}

    submesh_properties ['mean_quality'] = {id:float(quality) for id,quality in  obj.get_submeshes_quality_mean().items()}

    # Convert the dictionary to a JSON string
    json_data = json.dumps(submesh_properties, indent=3)

    print('step:',3)   
         
    del submesh_properties

    graph_file = ''.join([path,id,'_'.join([preprocessed,'submesh-params.json'])])

    # Save the JSON string to a file
    with open(graph_file, 'w') as f:
        f.write(json_data)      

    del json_data

def submeshes_area_procedure (obj,**kwargs): 

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelfilepath = kwargs ['labelfilepath']

    print('step:',1)
    df_label = pd.read_csv(labelfilepath,skiprows=5,header=None,sep=' ',names=['a','b'],dtype=int)  

    df_label = dict(zip(df_label.a, df_label.b))

    labels =  get_uniquelabel_vertlist (df_label)

    del df_label

    print('step:',2)

    tri = trimesh.load(''.join([path, id, preprocessed, '.ply']))

    tri_mesh = trimesh.Trimesh (vertices=tri.vertices,faces=tri.faces)

    del tri
    
    print('step:',3)

    # Creates a dictionary of with a ridge point and the neighbours with the same label
    submeshes = create_label_submeshes (tri_mesh,labels)
    
    print('step:',4)

    del tri_mesh, labels

    submesh_properties = {}

    submesh_properties ['area'] = {n:float(label[0].area) 
                                            for n,label in submeshes.items()
                                      }
    del submeshes

    print('step:',5) 

    # Convert the dictionary to a JSON string
    json_data = json.dumps(submesh_properties, indent=3)

    print('step:',6)

    del submesh_properties

    graph_file = ''.join([path,id,'_'.join([preprocessed,'submesh-params.json'])])

    # Save the JSON string to a file
    with open(graph_file, 'w') as f:
        f.write(json_data)      

    del json_data    