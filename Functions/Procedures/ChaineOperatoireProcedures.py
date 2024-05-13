# manual ChaineOperatoire
from Classes.BasicClasses import manualEdges

# @timing
def edge_to_arrow_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelfilepath = kwargs ['labelfilepath']
    exp_path = kwargs ['exp_path'] 
    circumference = kwargs ['circumference'] 
    radius = kwargs ['radius']
    manu_type = kwargs['manual_type']
    edge_name = kwargs['edge_name']

    # Data import and data preparation 
    obj.prep_polygraphs(path,id,preprocessed,labelfilepath,exp_path)
    obj.prep_ridges()

    # create node coordinates
    obj.get_centroids()

    mE = manualEdges()
    if manu_type == 'edges':
        mE.import_edges(path,''.join([id, edge_name]))
        
    elif manu_type == 'edges_nodes':
        mE.import_edges_nodes(path,''.join([id, edge_name]))

    else:
        print('no reference for edges provided')
        return          

    obj.edge_name = edge_name

    obj.manual_edges = mE.manual_edges
    del mE    

    obj.edges_to_ridgegraph()

    obj.direct_ridgegraph()

    obj.create_chaine_operatoire(circumference,radius)

    obj.create_chaine_operatoire_labels()

    obj.create_3D_label()
    # obj.create_chaine_operatoire_functvals(manu_type)
    # obj.export_chaine_operatoire_functvals (obj.vert_dict)

    obj.export_DiG_gexf()
