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
                                                        self.preprocessed,
                                                        '_'.join([  '',
                                                                    'ridge-labels'])
                                                        ]))

    def scar_to_ridge_labels_CC (self):

        """
        Creates a txt label of the label outlines and the other label points. 
        """   

        self.temp_dict_label = self.dict_label.copy()

        self.ridge_neighbour_shared_label.values()

        ridge_vertices = self.ridge_neighbour_shared_label.keys()

        ridge_label = max(self.unique_labels)+1

        for key in ridge_vertices:
            self.temp_dict_label[key] = ridge_label


        write_labels_txt_file (self.temp_dict_label, ''.join ([ self.path, 
                                                        self.id,
                                                        self.preprocessed,                                                  
                                                        '_'.join([  '',
                                                                    'ridge-labels-CC'])
                                                        ]))
        

    def merge_labels (self,neighbors_dict,labels, merge_label):

        i = 0

        while [label for label in labels.values() if label == merge_label]:
            for vert,label in labels.items():
                if label == merge_label:
                    max_list = [labels[neigh] 
                                for neigh in  neighbors_dict[vert] 
                                    if labels[neigh] != merge_label]
                    try:
                        labels[vert] = max(set(max_list), key = max_list.count)      
                    except:
                        print(vert)   

            i += 1

            if i == 10:
                break                          

        return labels

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
        # neigh_label_list = list([item for vals in self.ridge_neighbour_notshared_label.values() for item in vals])
        ridge_label = 1#max(set(neigh_label_list), key = neigh_label_list.count)

        # filtering for all vertices with ridge label
        ridge_vertices = [vert for vert,labels in notshared_label.items() if ridge_label not in labels]

        # creating a temp copy to adjust to filtering
        temp_dict_label = self.dict_label.copy()

        # relabelling outline ridge vertices to max labels of neigh labels 
        for r_vert in ridge_vertices:

            try:
                temp_dict_label[r_vert] = max(set(notshared_label[r_vert][:-1]), key = notshared_label[r_vert][:-1].count) 
            except: 
                temp_dict_label[r_vert] = max(set(notshared_label[r_vert]), key = notshared_label[r_vert].count) 


        # Filter for remaining isolated ridge labels as long vertices have ridge label
        print('Ridge_label:', ridge_label)
        # i = 0
        temp_dict_label = self.merge_labels(self.vertex_neighbors_dict,temp_dict_label, ridge_label)

        # while [label for label in temp_dict_label.values() if label == ridge_label]:

        #     for vert,label in temp_dict_label.items():
        #         if label == ridge_label:
        #             max_list = [temp_dict_label[neigh] 
        #                                                 for neigh in  self.vertex_neighbors_dict[vert] 
        #                                                     if temp_dict_label[neigh] != ridge_label]
                    
        #             try:
        #                 temp_dict_label[vert] = max(set(max_list), key = max_list.count)    

        #             except:
        #                 print(vert)
        #     i += 1

        #     if i == 10:
        #         break      

        unique_labels = np.unique([v for v in temp_dict_label.values()])

        small_label = []

        for unique_label in unique_labels:
            length = len([v for v in temp_dict_label.values() if v == unique_label])
            if length < self.tresh:
                small_label.append(unique_label) 

        for sl in small_label: 
            
            temp_dict_label = self.merge_labels(self.vertex_neighbors_dict,temp_dict_label, sl)

            # while [label for label in temp_dict_label.values() if label == sl]:
            #     for vert,label in temp_dict_label.items():
            #         if label == sl:
            #             max_list = [temp_dict_label[neigh] 
            #                         for neigh in  self.vertex_neighbors_dict[vert] 
            #                             if temp_dict_label[neigh] != sl]
            #             try:
            #                 temp_dict_label[vert] = max(set(max_list), key = max_list.count)      
            #             except:
            #                 print(vert)          

            #     i += 1

            #     if i == 10:
            #         break   


        dict_label = {n+1: [vert for vert,label in temp_dict_label.items() if label == v] for n,v in enumerate(unique_labels)}

        temp_dict_label = {vert:label for label, vals in dict_label.items() for vert in vals}

        # Write scar label file
        write_labels_txt_file (temp_dict_label, ''.join ([ self.path, 
                                                        self.id,
                                                        self.preprocessed,                                                     
                                                        '_'.join([  '',
                                                                    'scar-labels'])
                                                        ]))        