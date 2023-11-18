import pymeshlab
import numpy as np
import pandas as pd
import time 
import python_libs.write_labels_txt as jan

# function to determine ridge points after segmentation

def ridgedetection (path,name):
    
    time_begin = time.time()
    
    # define variables
    filename = path + name + ".ply" # 3D file of the model
    labelname = path + name + ".txt" #  label of the segmentation
    df_labels = pd.read_csv(labelname,skiprows=5,header=None) # import txt segmentation 
    
    # importing 3D model
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(filename)
    
    # separate faces and point cloud
    faces = ms.current_mesh().face_matrix().tolist()
    vertices = ms.current_mesh().vertex_matrix().tolist()
    
    #redefine faces as ndarray
    faces = np.array(faces)
    
    # create a ndarray of all individual edges between points bidirectional
    np.stack((faces [:,0],faces [:,1]), axis=1),np.stack((faces [:,1],faces [:,2]), axis=1),np.stack((faces [:,0],faces [:,2]), axis=1),
    np.stack((faces [:,1],faces [:,0]), axis=1),np.stack((faces [:,2],faces [:,1]), axis=1),np.stack((faces [:,2],faces [:,0]), axis=1)

    data = np.concatenate((np.stack((faces [:,0],faces [:,1]), axis=1),np.stack((faces [:,1],faces [:,2]), axis=1),
                           np.stack((faces [:,0],faces [:,2]), axis=1),np.stack((faces [:,1],faces [:,0]), axis=1),
                           np.stack((faces [:,2],faces [:,1]), axis=1),np.stack((faces [:,2],faces [:,0]), axis=1)), 
                           axis=0)
    # transform to a DataFrame
    df = pd.DataFrame(data)

    # drop duplicated coonections
    df = df.drop_duplicates()
    
    # create a list of labels, append rows and transform to DataFrame
    label_list =  []

    for pid,label in enumerate(df_labels[0]):
        label_list.append(label.split(' '))

    df_label = pd.DataFrame (label_list,columns=['a','b'])
    
    # create dictionaries of a point and their adjacent points (df_dict), and of point and their adjacent labels
    df_dict = {}
    df_label_dict = {}

    for key,v in enumerate(vertices):
        df_dict[key] = list(df[df[0] == key][1])
    
    # finding ridge points by looking whether the points label and or adjacent labels are different. If yes, it's a ridge point.
    ridge_key = []
    ridge_key_infos = []

    df_label_dict = dict(zip(df_label.a, df_label.b))

    for key,v in enumerate(vertices):
        value = []

        for v in df_dict[key]:
            value.append(df_label_dict [str(v)])

        value = value + [df_label_dict [str(key)]]
        unique_labels = '' 
        
        for n,i in enumerate (np.unique(value)):
            if n == 0:
                unique_labels = str(i) 
            else: 
                unique_labels = unique_labels + ',' +  str(i) 
        ridge_key_infos.append([key,unique_labels]) 
        
        
        if len(np.unique(value)) > 1:        
            ridge_key.append([key,2])
            
        else:        
            ridge_key.append([key,1])
       
   
    #################################################
    # saving ridge points and the labels in different files.
    ridge_dict = dict(ridge_key)
    ridge_infos_dict = dict(ridge_key_infos)
    
    jan.write_labels_txt_file (ridge_dict,path + name + '_ridge')  
    jan.write_labels_txt_file (ridge_infos_dict,path + name + '_ridge_info')  
    #pd.DataFrame([ridge_infos_dict]).to_csv(path + name + '_ridge_info',sep=',')
    print(time.time()-time_begin)
