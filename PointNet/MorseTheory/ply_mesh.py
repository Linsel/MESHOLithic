import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'MorseTheory'))

from mesh import Mesh
from Algorithms.LoadData.Datastructure import Vertex, Edge, Face
from Algorithms.LoadData.read_ply import read_ply#, read_normals_from_ply
from Algorithms.LoadData.read_funvals import read_funvals
from Algorithms.ProcessLowerStars import ProcessLowerStars

from PlotData.write_labels_txt import write_labels_txt_file, write_labels_params_txt_file, write_funval_thresh_labels_txt_file
from PlotData.write_pline_file import write_pline_file, write_pline_file_thresholded

import timeit
import os
import numpy as np

import os
duration = 1  # seconds
freq = 440  # Hz


from sklearn.cluster import MeanShift

from Segmentation.Meanshift import MeanShiftClusteringLabels
from Statistics.MahalanobisDist import MahalanobisDist


class Ply_Mesh (Mesh):
    
    def init (self, label_array=None):
        super(self).__init__()
        self.label_array = label_array

    def load_ply(self, filename, quality_index):
        read_ply(filename, quality_index, self.Vertices, self.Edges, self.Faces, self.Links)
        self.filename = os.path.splitext(filename)[0]
        
    def assign_labels(self):
        
        assign_label 
    
    def MahalanobisDist(self,point_cloud,variable_list,variable_filter):
        
        for variable in variable_filter:

            a = point_cloud [:,variable_list[variable]] 

            a = a[np.newaxis].T

            a[np.isnan(a)] = 0


            if 'values' not in locals():

                values =  np.array((a)) 

            else:

                values =  np.c_[(values,a)]#, axis=1) 
        
        
        mal  = MahalanobisDist(values, verbose=False)

        mahalanobis = np.array(mal)

        return mahalanobis[np.newaxis].T

    
    def calculate_meanshift (self, point_cloud, variable_list, variable_filter_list, recursive_depth, bandwidth):
        
        for num, variable_filter in enumerate(variable_filter_list):
            
            for variable in variable_filter:

                if num != 0:

                    a = point_cloud [:,variable_list[variable]] 

                    a = a[np.newaxis].T

                    a[np.isnan(a)] = 0


                    if 'values' not in locals():

                        values =  np.array((a)) 

                    else:

                        values =  np.c_[(values,a)]#, axis=1) 

                else:

                    b = point_cloud [:,variable_list[variable]] 

                    b = b[np.newaxis].T

                    b[np.isnan(b)] = 0


                    if 'values_maha' not in locals():

                        values_maha =  np.array((b)) 

                    else:

                        values_maha =  np.c_[(values_maha,b)]
            
        
        for rep in range(1,recursive_depth):             
            start_total_time = timeit.default_timer()
            start_time = timeit.default_timer()
            
            label = np.array ([1,1,1,1,1,1,1,1,1,2,1])
            
            if 'label_array' not in locals():
                
                band_width = 1
                
                labels =  MeanShiftClusteringLabels (values, band_width)
                
                print(labels)
                
                label_array = np.array(([x + 1 for x in labels] ))[np.newaxis].T 
                
                #label_array = [x+1 for x in label_array][np.newaxis].T
                
                
                print(label_array.shape)
            
            elif 'label_array' in locals():

                index = np.arange(label_array.shape[0])[np.newaxis].T # create index array for indexing 
                
                if rep == 2:
                
                    array_with_indices = label_array[:]
                    
                else: 

                    array_with_indices = label_array[:,rep-1][np.newaxis].T                
                
                
#                 print(index.shape)
#                 print(array_with_indices.shape)
                    
                array_with_indices = np.concatenate((index,array_with_indices ), axis=1) 
                
                #if rep == 2:
                
                label = labels

                for count, i in enumerate (np.unique (array_with_indices[:,1])):
                    
                    print(len(values [array_with_indices[:,1] == i,]))
                    
                    if len(values [array_with_indices[:,1] == i,]) >= 1000:
                        
                        if rep == 2:
                            
                            labels = MeanShiftClusteringLabels(values [array_with_indices[:,1] == i,],bandwidth)
                            
                            i_max = max(np.unique(labels))
                            
                            print(i_max)
                        
                        else:
                        
#                             if np.unique (label_array[:,rep-1][np.newaxis].T).all() == np.unique (label_array[:,rep-2][np.newaxis].T).all():

#                                 #labels = MeanShiftClusteringLabels(values_maha [array_with_indices[:,1] == i,],bandwidth)
#                                 labels = array_with_indices[array_with_indices[:,1] == i,1]
                            i_max_thres = -int(int(rep)-2)
    
#                             if rep != i_max:
                                
#                                 labels = MeanShiftClusteringLabels(values_maha [array_with_indices[:,1] == i,],bandwidth) 
                            
#                             else: 

                            labels = MeanShiftClusteringLabels(values [array_with_indices[:,1] == i,],bandwidth)                                                           
                    
                        labels_import = np.array(([str(i) + str(x + 1) for x in labels])) # [np.newaxis].T

                        array_with_indices[array_with_indices[:,1] == i,1] = labels_import # + 100 + label
                        

                        
                        
                
#                 print(np.unique(array_with_indices[:,1]))

                label_array = np.concatenate((label_array,array_with_indices[:,1][np.newaxis].T), axis=1) 

                print(str(rep) + ':' + str(i))
                    
                #else:

                        
#                     for count, i in enumerate (np.unique (label_array[:,rep-2])):


#                         #label = MeanShiftClusteringLabels(values [array_with_indices[:,1] == i],bandwidth)

#                         label = np.array(([x + 100 for x in label]))  [np.newaxis].T

#                         array_with_indices[array_with_indices[:,1] == i,1] = label 

                        
                label_array = np.concatenate((label_array,array_with_indices[:,1][np.newaxis].T), axis=1) 
                self.label_array = label_array   
                
                
            end_total_time = timeit.default_timer() - start_total_time
            print('Time per run:', end_total_time)
        
        self.label_array = label_array          