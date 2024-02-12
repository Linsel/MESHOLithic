import os,sys

currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from util import *


from DetermineRidges.RidgeAnalysis import LabelledMesh
from DetermineRidges.TransformLabelledMesh import TransformLabelledMesh
from Classes.Graph.GraphPlotting import ChaineOperatoire,GraphEvaluation


from IntegralInvariants.II1DClasses import MSIIChaineOperatoire


# import timing function decorator  
from Functions.EssentialDecorators import timing

# labelled meshes 
from Functions.Procedures.LabbelledMeshProcedures import ridge_prepare_procedure,kmeans_label_procedure,kmeans_slice_procedure,label_slice_procedure,export_ridges_mesh_procedure,direct_graph_area_procedure
from Functions.Procedures.SubmeshesProcedures import submeshes_procedure, submeshes_properties_procedure


from Functions.Procedures.TransformLabbelledMeshProcedures import scar_to_ridge_labels_binary_procedure,scar_to_ridge_labels_CC_procedure,ridge_CC_to_scar_labels_procedure

# Graph procedures
from Functions.Procedures.MSIIChaineOperatoireProcedures import CO_prepare_procedure,MSII_procedure,MSII_feature_vector_procedure
from Functions.Procedures.GraphEvaluationProcedures import undirected_graph_procedure,graph_evaluation_procedure,graph_direct_parameter_procedure,direct_graph_procedure
from Functions.Procedures.ChaineOperatoireProcedures import edge_to_arrow_procedure


#________________________
# labbeldMesh procedures

@timing
def labelledmesh_procedures (method,**kwargs):
   
    LM = LabelledMesh()

    procedures = {'ridge_prepare':ridge_prepare_procedure,
                  'kmeans_label':kmeans_label_procedure,
                  'kmeans_sclice':kmeans_slice_procedure, 
                  'label_slice':label_slice_procedure,
                  'direct_graph_area':direct_graph_area_procedure,
                  'export_ridges_mesh':export_ridges_mesh_procedure,
                  'submeshes':submeshes_procedure,
                  'submeshes_properties':submeshes_properties_procedure}

    func = procedures.get(method)

    func(LM,**kwargs)

    return LM

@timing
def transform_labelledmesh_procedures (method,**kwargs):
   
    TLM = TransformLabelledMesh()

    procedures = {'scar_to_ridge_labels_binary':scar_to_ridge_labels_binary_procedure,
                  'scar_to_ridge_labels_CC':scar_to_ridge_labels_CC_procedure,
                  'ridge_CC_to_scar_labels':ridge_CC_to_scar_labels_procedure}

    func = procedures.get(method)

    func(TLM,**kwargs)

    return TLM

#____________________________
# MSII based procedures

@timing
def MSII_chaineoperatoire_procedures (method,**kwargs):
   
    CO = MSIIChaineOperatoire()

    procedures = {'CO_prepare':CO_prepare_procedure,
                  'MSII':MSII_procedure,
                  'MSII_feature_vector':MSII_feature_vector_procedure}

    func = procedures.get(method)

    func(CO,**kwargs)

    return CO

#____________________________
# Evaluation

@timing
def graph_procedures (method,**kwargs):

    GE = GraphEvaluation ()

    procedures = {'undirected_graph':undirected_graph_procedure,
                  'graph_evaluation':graph_evaluation_procedure,
                  'graph_direct_parameter':graph_direct_parameter_procedure,
                  'direct_graph':direct_graph_procedure}

    func = procedures.get(method)

    func(GE,**kwargs)

    return GE    

@timing
def co_procedures (method,**kwargs):

    CO = ChaineOperatoire ()

    procedures = {'edge_to_arrow':edge_to_arrow_procedure}

    func = procedures.get(method)

    func(CO,**kwargs)

    return CO        
