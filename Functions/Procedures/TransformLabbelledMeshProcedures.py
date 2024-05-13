import os,sys

currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
pparentdir = os.path.dirname(parentdir)
sys.path.insert(0, currentdir) 
sys.path.insert(0, parentdir) 
sys.path.insert(0, pparentdir) 

from util import *

# compare two operational sequences 
from Functions.EvaluateGraph import directed_edges_parameters

from Functions.EssentialEdgesFunctions import get_manual_edges

# import timing function decorator  
from Functions.EssentialDecorators import timing

from minions.LabelMinions import color_to_labels,color_to_label #as color_to_binary_label
# from minions.MorseMeshMinions import color_to_labels as color_to_labels

from LabbelledMeshProcedures import update_label_procedure

@timing
def ridge_prepare_procedure (obj,**kwargs):

    path = kwargs ['path'] 
    id = kwargs ['id']
    preprocessed = kwargs ['preprocessed']
    labelfilepath = kwargs ['labelfilepath']
    obj.ridge_label = kwargs ['ridge_label']    
    

    # Data import and data preparation 
    obj.load_labelled_mesh (path, id, preprocessed, labelfilepath)

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

    obj.tresh = kwargs ['tresh']

    obj.ridge_CC_to_scar_labels()

@timing
def color_to_scar_labels_procedure(obj,**kwargs):

    # method = ''.join([parentdir,'/../minions/MorseMeshMinions/color_to_labels.py'])
    # kwargs.update({'method':method})

    # color_to_label(**kwargs)

    #####

    method = ''.join([parentdir,'/../minions/ColorMinions/color_to_labels.py'])
    kwargs.update({'method':method})

    # color_to_label(**kwargs)
    color_to_labels (**kwargs)

    CC_label = ''.join([kwargs['path'], kwargs['id'],kwargs['preprocessed'],'_CC-labels.txt'])

    kwargs.update({'labelfilepath':CC_label})

    ridge_CC_to_scar_labels_procedure(obj,**kwargs)

    # save CC-labels and scar-labels also as ply files

    update_label_procedure(obj,**kwargs)

    scar_label = ''.join([kwargs['path'], kwargs['id'],kwargs['preprocessed'],'_scar-labels.txt'])

    kwargs.update({'labelfilepath':scar_label})


    update_label_procedure(obj,**kwargs)


@timing
def ridge_to_scar_labels_procedure(obj,**kwargs):

    # method = ''.join([parentdir,'/../minions/MorseMeshMinions/color_to_labels.py'])
    # kwargs.update({'method':method})

    # color_to_label(**kwargs)

    #####

    ridge_CC_to_scar_labels_procedure(obj,**kwargs)

    # save CC-labels and scar-labels also as ply files

    update_label_procedure(obj,**kwargs)

    scar_label = ''.join([kwargs['preprocessed'],'_scar-labels'])

    kwargs.update({'labelname':scar_label})

    update_label_procedure(obj,**kwargs)