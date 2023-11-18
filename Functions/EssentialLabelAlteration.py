from util import *

def get_unique_labels (labels):

    """
    Extracts unique labels from vertex:label dictionary

    Args:
        labels (dict): Contains vertex:label dictionary

    Returns:
        ul (set): Set of unique labels/ values

    """    
    ul = {val for val in labels.values()}

    return ul

def get_uniquelabel_vertlist (labels):
    """
    Transforms vertex:label dictionary to unique-labels:vertexlist dictionary 

    Args:
        labels (dict):  Contains a dictionary where vertex_id is the key and its label saved as integer is the value.
    
    Returns: 
        labels_vertices (dict): Dictionary which contains labels as keys and vertex ids as list (values)
    
    """

    unique_labels = get_unique_labels (labels)

    labels_vertices = {ul:[n for n,label in labels.items() if label == ul] for ul in unique_labels}
    
    return labels_vertices

def get_labels_IoU_max (label_a,label_o):
    """
    Finds an interception over union pair with the highest amount of vertices belonging to one label_a-label_o pairs an assigns label_o-vertex list (values) to label_a label (key). 

    Args:
        label_a (dict): contains labels (output key), to which vertices from label_o will be ordered. 
        label_o (dict): contains vertices (output value), which will be assigned to label_a-label according to the maximum IoU.  

    Returns:
        max_lab (dict): reassigned dictionary, where label_a:label is the key and the reassigned label_o:vertices are the values.  

    """

    label_a_ul_vertl = get_uniquelabel_vertlist (label_a)

    # interception over union of the label_a and the label_o labels    
    counter = get_labels_IoU (label_a,label_o)

    max_lab = {label:[] for labs in counter.values() for label in labs}

    for label, stats in counter.items():

        maxlab = max(stats, key=stats.get)

        [max_lab [maxlab].append (id) for id in label_a_ul_vertl[label]] 



    return max_lab

def get_labels_IoU (label_a,label_o):

    """
    Calculates an interception over union of the label_a and the label_o labels (values) and calculates the label_a:label_o vertices amounts. 

    Args:
        label_a (dict): dictionary with a vertex:label key-value pair and source of the outer part of the later nested dictionary.
        label_o (dict): dictionary with a vertex:label key-value pair and source of the inner part of the later nested dictionary.

    
    Returns:
        counter (dict): Contains a nested dictionary with a label_a:key as key and in values a second dictionary. This nested dictionary contains label_o:key as 
                        key and the number of vertices belonging to both a label_a:key and a label_o:key.
    """


    unique_labels = get_unique_labels(label_o)

    # prepare counter for how many vertices belonging to the labela-label_o pairs
    counter = {val:{label:0 for label in unique_labels} for val in label_a.values()}
    
    # interception over union of the label_a and label_o labels
    for vert,label in label_a.items():
        counter[label][label_o[vert]] += 1

    return counter

def label_vertices (obj, start, vertices, labels, data_name):

    num_vert = len(vertices) / len(labels)

    labelled = {}

    for num,label in enumerate(labels):

        labelled.update ({vert + start + len(labelled.keys()):label 
                            for vert,_ in enumerate(vertices[
                                int(num * num_vert):
                                int((num + 1) * num_vert)])
                    })

    write_labels_txt_file (labelled, ''.join([obj.path, 
                                              obj.id, 
                                              obj.processed, 
                                              data_name]))

