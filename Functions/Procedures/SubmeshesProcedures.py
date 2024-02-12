

def submeshes_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelname = kwargs ['labelname']
    exp_path = kwargs ['exp_path'] 

    obj.load_labelled_mesh(path,id,preprocessed,labelname,exp_path) 

    obj.get_quality()

    obj.get_label_submeshes()    
    
    return obj

def submeshes_properties_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelname = kwargs ['labelname']
    exp_path = kwargs ['exp_path'] 

    obj.load_labelled_mesh(path,id,preprocessed,labelname,exp_path) 

    obj.get_quality()

    obj.get_label_submeshes()    
    
    obj.submesh_properties = {}

    obj.submesh_properties ['area'] = {n:label[0].area 
                                            for n,label in obj.submeshes.items()
                                      }

    obj.submesh_properties ['mean_quality'] = obj.get_submeshes_quality_mean ()
    
    return obj
