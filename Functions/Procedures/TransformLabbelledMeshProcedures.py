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
def scar_to_ridge_labels_binary_procedure(obj,**kwargs):

    ridge_prepare_procedure (obj,**kwargs)

    obj.scar_to_ridge_labels_binary()

@timing
def scar_to_ridge_labels_CC_procedure(obj,**kwargs):

    ridge_prepare_procedure (obj,**kwargs)

    obj.scar_to_ridge_labels_CC()

@timing
def ridge_CC_to_scar_labels_procedure(obj,**kwargs):

    ridge_prepare_procedure (obj,**kwargs)

    obj.ridge_CC_to_scar_labels()
