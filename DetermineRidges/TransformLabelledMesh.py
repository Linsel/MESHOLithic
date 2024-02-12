import os,sys

currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from util import *

from DetermineRidges.RidgeAnalysis import LabelledMesh


# handeling of labelled meshes, extracting the outline 
class TransformLabelledMesh (LabelledMesh):
    """
    This class transforms two kind of labels ridges-CC and scars in eachother, relying on the LabelledMesh class.
    """

    def __init__(self, 
                 label_name: str = None):
        
        """
        Super Init LabelledMesh.

        Args:

        """

        super().__init__(label_name)            


    def scar_to_ridge_labels_binary (self):

        """
        Creates a txt label of the label outlines. 
        """   

        temp_dict_label = self.dict_label.copy()

        self.ridge_neighbour_shared_label.values()

        ridge_vertices = self.ridge_neighbour_shared_label.keys()

        for key in self.dict_label.keys():
            if key in ridge_vertices:
                temp_dict_label[key] = 1
            else:
                temp_dict_label[key] = 2

        write_labels_txt_file (temp_dict_label, ''.join ([ self.path, 
                                                        self.id,
                                                        '_'.join([  '',
                                                                    'ridge-labels'])
                                                        ]))

    def scar_to_ridge_labels_CC (self):

        """
        Creates a txt label of the label outlines and the other label points. 
        """   

        temp_dict_label = self.dict_label.copy()

        self.ridge_neighbour_shared_label.values()

        ridge_vertices = self.ridge_neighbour_shared_label.keys()

        ridge_label = max(self.unique_labels)+1

        for key in ridge_vertices:
            temp_dict_label[key] = ridge_label


        write_labels_txt_file (temp_dict_label, ''.join ([ self.path, 
                                                        self.id,
                                                        '_'.join([  '',
                                                                    'ridge-labels-CC'])
                                                        ]))
        
    def ridge_CC_to_scar_labels (self):

        """
        Transforms ridge CC labels to scar labels. Two step approach, first, relabelling outline of ridge label, second, iterative relabelling 
        of remaining Vertices with ridge labelling. 
        
        Reasoning: Relying only on second step, could lead to unintenional growing labels and first step is not iterable due to . 
            
        Limitations: Predefined labels are not necessary. Binary labelling of scars and labels are not allowed.

        """

        # Filtering for ridge points (keys) and a list of all neighboring vertex labels which are dissimilar to the key vertex label  
        notshared_label = {key: [self.dict_label[v] for v in self.vertex_neighbors_dict[key] + [self.dict_label[key]] 
                                                if self.dict_label[key] != self.dict_label[v]]
                                                
                                        
                                        for key, v in enumerate(self.vertices) 
                                                if len(np.unique([self.dict_label[v] 
                                                    for v in self.vertex_neighbors_dict[key]] + [self.dict_label[key]])) > 1
                                            }   

        # filtering for most often neighboring label -> ridge label
        neigh_label_list = list([item for vals in self.ridge_neighbour_notshared_label.values() for item in vals])
        ridge_label = max(neigh_label_list)

        # filtering for all vertices with ridge label
        ridge_vertices = [vert for vert,labels in notshared_label.items() if ridge_label not in labels]

        # creating a temp copy to adjust to filtering
        temp_dict_label = self.dict_label.copy()

        # relabelling outline ridge vertices to max labels of neigh labels 
        for r_vert in ridge_vertices:

            temp_dict_label[r_vert] = max(notshared_label[r_vert][:-1])   


        # Filter for remaining isolated ridge labels as long vertices have ridge label
        print('Ridge_label:', ridge_label)
        i = 0
        while [label for label in temp_dict_label.values() if label == ridge_label]:

            for vert,label in temp_dict_label.items():
                if label == ridge_label:
                    try:
                        temp_dict_label[vert] = max([temp_dict_label[neigh] for neigh in  self.vertex_neighbors_dict[vert] if temp_dict_label[neigh] != ridge_label])
                    except:
                        print(vert)
            i += 1

            if i == 10:
                break


        for vert,label in temp_dict_label.items():
            if label == ridge_label:
                try:
                    temp_dict_label[vert] = max([temp_dict_label[neigh] for neigh in  self.vertex_neighbors_dict[vert] if temp_dict_label[neigh] != ridge_label])       
                except:
                    print(vert)

        # Write scar label file
        write_labels_txt_file (temp_dict_label, ''.join ([ self.path, 
                                                        self.id,
                                                        '_'.join([  '',
                                                                    'scar-labels'])
                                                        ]))        