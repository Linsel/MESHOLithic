import os,sys

currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

pparentdir = os.path.dirname(parentdir)
sys.path.insert(0, pparentdir) 

from util import *


from DetermineRidges.RidgeAnalysis import LabelledMesh
from DetermineRidges.TransformLabelledMesh import TransformLabelledMesh
from Classes.Graph.GraphPlotting import ChaineOperatoire,GraphEvaluation
from Classes.Paths import Paths


from IntegralInvariants.II1DClasses import MSIIChaineOperatoire


# import timing function decorator  
from Functions.EssentialDecorators import timing



# labelled meshes 
from Functions.Procedures.LabbelledMeshProcedures import ridge_prepare_procedure,kmeans_label_procedure,kmeans_slice_procedure,label_slice_procedure,centroids_NNs_procedure,export_ridges_mesh_procedure,direct_graph_area_procedure,update_label_procedure
from Functions.Procedures.SubmeshesProcedures import submeshes_procedure, submeshes_properties_procedure


from Functions.Procedures.TransformLabbelledMeshProcedures import scar_to_ridge_labels_binary_procedure,scar_to_ridge_labels_CC_procedure,ridge_CC_to_scar_labels_procedure,color_to_scar_labels_procedure,ridge_to_scar_labels_procedure

# Graph procedures
from Functions.Procedures.MSIIChaineOperatoireProcedures import CO_prepare_procedure,MSII_procedure,MSII_feature_vector_procedure,CO_concavity_procedure,CO_angle_procedure
from Functions.Procedures.GraphEvaluationProcedures import graph_undirected_procedure,graph_direct_procedure,graph_direct_parameter_procedure,graph_evaluate_procedure,graph_direct_network_parameter_procedure
from Functions.Procedures.ChaineOperatoireProcedures import edge_to_arrow_procedure

# Data processing
from Functions.Procedures.DataProcedures import merge_data_procedure,single_value_evaluation_procedure



# Image processing
from Functions.Procedures.ImageProcedures import annotation_image_procedure

# minions
from minions.GigaMeshMinions import command_line_GigaMesh,MSII_single_feature
from minions.MeshMinions import update_vertex_quality,update_vertex_label


#________________________
# labbeldMesh procedures

@timing
def labelledmesh_procedures (obj:LabelledMesh = None,
                             **kwargs):
   
    method = kwargs['method']
    # if obj == None:
    #     obj = LabelledMesh()

    procedures = {'ridge_prepare':ridge_prepare_procedure,
                  'kmeans_label':kmeans_label_procedure,
                  'kmeans_sclice':kmeans_slice_procedure, 
                  'label_slice':label_slice_procedure,
                  'direct_graph_area':direct_graph_area_procedure,
                  'export_ridges_mesh':export_ridges_mesh_procedure,
                  'submeshes':submeshes_procedure,
                  'submeshes_properties':submeshes_properties_procedure,
                  'update_label':update_label_procedure}

    func = procedures.get(method)

    func(obj,**kwargs)

    return obj

@timing
def transform_labelledmesh_procedures (obj:TransformLabelledMesh = None,
                                       **kwargs):

    # if obj == None:
    #     obj = TransformLabelledMesh()
    method = kwargs['method']

    procedures = {'scar_to_ridge_labels_binary':scar_to_ridge_labels_binary_procedure,
                  'scar_to_ridge_labels_CC':scar_to_ridge_labels_CC_procedure,
                  'ridge_CC_to_scar_labels':ridge_CC_to_scar_labels_procedure,
                  'color_to_scar_labels':color_to_scar_labels_procedure,
                  'ridge_to_scar_labels':ridge_to_scar_labels_procedure}

    func = procedures.get(method)

    func(obj,**kwargs)

    return obj

#____________________________
# MSII based procedures

@timing
def MSII_chaineoperatoire_procedures (obj:MSIIChaineOperatoire = None,
                                      **kwargs):
    
    method = kwargs['method']
    # obj = MSIIChaineOperatoire()

    procedures = {'CO_prepare':CO_prepare_procedure,
                  'MSII':MSII_procedure,
                  'CO-MSII-fv':MSII_feature_vector_procedure,
                  'CO-concavity':CO_concavity_procedure,
                  'CO-angle':CO_angle_procedure}

    func = procedures.get(method)

    func(obj,**kwargs)

    return obj

#____________________________
# Evaluation

@timing
def graph_procedures (  obj:GraphEvaluation = None,
                        **kwargs):
    
    method = kwargs['method']

    # obj = GraphEvaluation ()

    procedures = {'graph_undirected':graph_undirected_procedure,
                  'graph_evaluate':graph_evaluate_procedure,
                  'graph_direct_parameter':graph_direct_parameter_procedure,
                  'graph_direct_network_parameter':graph_direct_network_parameter_procedure,
                  'graph_direct':graph_direct_procedure}

    func = procedures.get(method)

    func(obj,**kwargs)

    return obj    

@timing
def co_procedures (obj:ChaineOperatoire = None,
                   **kwargs):

    method = kwargs['method']
    # obj = ChaineOperatoire ()

    procedures = {'edge_to_arrow':edge_to_arrow_procedure}

    func = procedures.get(method)

    func(obj,**kwargs)

    return obj        

def GigaMesh_procedures (obj: object = None, 
                           **kwargs):
    
    method = kwargs['method']

    procedures = {'command_line_GigaMesh':command_line_GigaMesh,
                  'gigamesh-clean':command_line_GigaMesh,
                  'gigamesh-featurevectors':command_line_GigaMesh,                  
                  'MSII_single_feature': MSII_single_feature}

    func = procedures.get(method)

    func(obj,**kwargs)

    return obj  

#
def helper_procedures ( obj: object = None, 
                        **kwargs):

    method = kwargs['method']

    procedures = {'gigamesh-featurevectors':command_line_GigaMesh,
                  'MSII_single_feature': MSII_single_feature}

    func = procedures.get(method)

    func(obj,**kwargs)

    return obj  

# 
def path_procedures (obj: object = None, 
                        **kwargs):
    
    method = kwargs['method']

    procedures = {  'init_path':init_path_procedure,
                    'generate_mesh':generate_mesh_procedure,
                    'shortest_path':shortest_path_procedure}

    func = procedures.get(method)

    obj = func(obj,**kwargs)

    return obj  

def image_procedures(obj: object = None, 
                        **kwargs):


    method = kwargs['method']

    procedures = {'annotation_image':annotation_image_procedure}

    func = procedures.get(method)

    func(obj,**kwargs)

    return obj  

def data_procedures(obj: object = None, 
                        **kwargs):


    method = kwargs['method']

    procedures = {'merge_data':merge_data_procedure,
                  'single_value_evaluation':single_value_evaluation_procedure}

    func = procedures.get(method)

    func(obj,**kwargs)

    return obj  

#
@timing
def procedures (obj: object = None, 
                **kwargs):
    
    
    class_type = kwargs['class']
    

    objects = { 'labelledmesh':LabelledMesh,
                'transform_labelledmesh':TransformLabelledMesh,
                'CO-MSII':MSIIChaineOperatoire,
                'GRAPH':GraphEvaluation,
                'CO':ChaineOperatoire,
                'GigaMesh':object,
                'Helpers':object,
                'PATH':Paths,
                'IMAGE':object,
                'DATA':object}

    if obj == None:
        obj_func = objects.get(class_type)
        obj = obj_func ()
        
    procedures = {'labelledmesh':labelledmesh_procedures,
                  'transform_labelledmesh':transform_labelledmesh_procedures,
                  'CO-MSII':MSII_chaineoperatoire_procedures,
                  'GRAPH':graph_procedures,
                  'CO':co_procedures,
                  'GigaMesh':GigaMesh_procedures,
                  'Helpers':helper_procedures,
                  'PATH':path_procedures,
                  'IMAGE':image_procedures,
                  'DATA':data_procedures}

    func = procedures.get(class_type)

    func(obj,**kwargs)

    del obj         