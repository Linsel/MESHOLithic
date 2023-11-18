# basic interface for importing meshes 
import os
import sys
import timeit
import math
from datetime import datetime, timezone
import time

# adding current and parent directory to paths
currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

import PythonLibs.writeLabelsTxt as jan

# Data structure
import numpy as np
import pandas as pd

# import networkx as nx
import logging
from Classes.ObjectClasses import Mesh

# Rotating matrices
from MeshAlteration.rotation import get_rotate_x, get_rotate_y, get_rotate_z, matrix_vector_multiply, get_flip_xz, has_axis_flip

# evaluate rotation
from MeshAlteration.evaluateRotation import combine_trafomat_gm, get_angle, compare_angle

# kMeans
from sklearn.cluster import KMeans

# 
class artefactOrientation (Mesh):
    
    def init (self, label_array=None):
        super(self).__init__()

    # Function to orientate mesh according to Palaeolithic blade orientation
    def create_trafomat(self):

        self.time_begin = time.time()   

        self.initial_orientation()

        t_1 = np.array(get_rotate_z(np.pi/2))
        t_1_gm = np.array(get_rotate_z(-np.pi/2)) 

        tri_mesh_export = self.tri_mesh.copy()

        for trafomat in np.stack((self.fit_trafomat,t_1)):
            # print(tri_mesh_export.vertex_normals[:3,:])
            tri_mesh_export.apply_transform(trafomat)


        # Calculate first the side by summing the normals in Y-direction to determine front side
        # try:
        self.prep_orientate_mesh_kmeans()              
        norm_zero = np.sum(tri_mesh_export.vertex_normals[self.klabels == 0][1])
        norm_one = np.sum(tri_mesh_export.vertex_normals[self.klabels == 1][1])
        zero =np.sum(self.curvature[self.klabels == 0])/len(self.curvature[self.klabels == 0])
        one = np.sum(self.curvature[self.klabels == 1])/len(self.curvature[self.klabels == 1])
        
        if norm_zero > norm_one: 
            if zero > one: 
                print(1)
                t_2 = np.array(get_rotate_y(2 * np.pi/2))
            else:
                t_2 = np.identity (4)
        elif norm_zero < norm_one: 
            if zero > one: 
                print(2)                
                t_2 = np.array(get_rotate_y(2 * np.pi/2))
            else:
                t_2 = np.identity (4)
        # except:
        #     print('Kmeans cluster of curvature is not calculatable for {}. Please check vertices whether they have all curvature values!'.format(self.name))
        #     t_2 = np.identity (4)

            
        if hasattr(self,'t_0'):
            self.trafomat_array = np.stack((self.fit_trafomat,self.t_0,t_1,t_2))
            self.trafomat_array_gm = np.stack((self.fit_trafomat,self.t_0,t_1_gm,t_2))
        else:
            self.trafomat_array = np.stack((self.fit_trafomat,t_1,t_2))
            self.trafomat_array_gm = np.stack((self.fit_trafomat,t_1_gm,t_2))            

        # tri_mesh_temp.apply_transform(trafomat_t2).export(self.path + self.name + '_traform_2.ply')        

        print(time.time()-self.time_begin)            

    def initial_orientation(self):

        self.fit_trafomat = self.fit_transform()

        det = np.linalg.det(self.fit_trafomat)

        if det < 0:
            t_0 = np.array(get_flip_xz())
            self.t_0 = t_0
        
        # Export initial orientation including possible flipped
        tri_mesh_temp = self.tri_mesh.copy()
        if 't_0' in locals():
            tri_mesh_temp.apply_transform(self.fit_trafomat).apply_transform(self.t_0).export(self.path + self.exp_path + self.name + '_O.ply')
        else:
            tri_mesh_temp.apply_transform(self.fit_trafomat).export(self.path + self.exp_path + self.name + '_O.ply')
        del tri_mesh_temp 

    def fit_transform(self):
        """
        Assumes observations in X are passed as rows of a numpy array.
        """

        # calculate the center of mass of the mesh
        center_of_mass = np.mean(self.vertices, axis=0)
        
        # calculate the covariance matrix
        cov_matrix = np.cov(self.vertices, rowvar=False)

        # calculate the eigenvalues and eigenvectors
        eigen_values, eigen_vectors = np.linalg.eigh(cov_matrix)

        # sorting eigenvectors based on their eigenvalues
        eig_values_index = np.argsort(eigen_values)[::-1]
        eig_vectors = eigen_vectors[:, eig_values_index]

        # translate the PCA transformed mesh data back to the original center_of_mass
        
        center_of_mass = np.array(center_of_mass)

        # create the transformation matrix
        trafomat = np.vstack((np.vstack((eig_vectors,center_of_mass)).T, np.array([0,0,0,1])))

        return trafomat
            
    def exp_trafomat(self):
        self.exp_trafo_list = []
        for trafomat in self.trafomat_array:
            self.exp_trafo_list.append('#------------------------------------------------------')
            self.exp_trafo_list.append('# Transformation applied to "' + self.name + '"')
            self.exp_trafo_list.append('#......................................................')
            self.exp_trafo_list.append(' '.join(["{:.6f}".format(x).replace('.', ',') for x in list(trafomat[0,:])]))
            self.exp_trafo_list.append(' '.join(["{:.6f}".format(x).replace('.', ',') for x in list(trafomat[1,:])]))
            self.exp_trafo_list.append(' '.join(["{:.6f}".format(x).replace('.', ',') for x in list(trafomat[2,:])]))        
            self.exp_trafo_list.append(' '.join(["{:.6f}".format(x).replace('.', ',') for x in list(trafomat[3,:])]))  
            self.exp_trafo_list.append('#......................................................')
            self.exp_trafo_list.append('# on ' + str(datetime.now().strftime("%A")) + ' ' + str(datetime.now().strftime('%A')[:2]) + ' ' + 
            str(datetime.now().strftime("%d")) + ' ' + str(datetime.now().strftime("%b")) + ' ' + str(datetime.now().strftime("%Y")) + 
            ' ' + str(datetime.now().strftime("%H:%M:%S")) + ' ' + str(datetime.now().astimezone().tzname()))
            self.exp_trafo_list.append('#------------------------------------------------------') 
            self.exp_trafo_list.append('') 

        # example:
        #------------------------------------------------------
        # Transformation applied to "' + self.name + '"'
        #......................................................
        # 0,833741 0,241975 -0,496309 21,978296
        # -0,167612 0,967358 0,190066 -91,278023
        # 0,526100 -0,075279 0,847084 -7,023476
        # 0,000000 0,000000 0,000000 1,000000
        #......................................................
        # on Donnerstag Do 08 Dez 2022 17:44:48 CET
        #------------------------------------------------------
        with open("{0}{1}_trafomat.txt".format(self.path + self.exp_path,self.name), "w") as output:
            for row in self.exp_trafo_list:
                output.write(str(row)+"\n")            
    
    def exp_trafomat_GMO(self):
        self.exp_trafo_list = []
        for n,trafomat in enumerate(self.trafomat_array_gm):
            # if n == 0:
            trafomat[:3,:3] = trafomat[:3,:3].T

            self.exp_trafo_list.append('#------------------------------------------------------')
            self.exp_trafo_list.append('# Transformation applied to "' + self.name + '"')
            self.exp_trafo_list.append('#......................................................')
            self.exp_trafo_list.append(' '.join(["{:.6f}".format(x).replace('.', ',') for x in list(trafomat[0,:])]))
            self.exp_trafo_list.append(' '.join(["{:.6f}".format(x).replace('.', ',') for x in list(trafomat[1,:])]))
            self.exp_trafo_list.append(' '.join(["{:.6f}".format(x).replace('.', ',') for x in list(trafomat[2,:])]))        
            self.exp_trafo_list.append(' '.join(["{:.6f}".format(x).replace('.', ',') for x in list(trafomat[3,:])]))  
            self.exp_trafo_list.append('#......................................................')
            self.exp_trafo_list.append('# on ' + str(datetime.now().strftime("%A")) + ' ' + str(datetime.now().strftime('%A')[:2]) + ' ' + 
            str(datetime.now().strftime("%d")) + ' ' + str(datetime.now().strftime("%b")) + ' ' + str(datetime.now().strftime("%Y")) + 
            ' ' + str(datetime.now().strftime("%H:%M:%S")) + ' ' + str(datetime.now().astimezone().tzname()))
            self.exp_trafo_list.append('#------------------------------------------------------') 
            self.exp_trafo_list.append('') 

        # example:
        #------------------------------------------------------
        # Transformation applied to "' + self.name + '"'
        #......................................................
        # 0,833741 0,241975 -0,496309 21,978296
        # -0,167612 0,967358 0,190066 -91,278023
        # 0,526100 -0,075279 0,847084 -7,023476
        # 0,000000 0,000000 0,000000 1,000000
        #......................................................
        # on Donnerstag Do 08 Dez 2022 17:44:48 CET
        #------------------------------------------------------
        with open("{0}{1}_GMO_trafomat.txt".format(self.path + self.exp_path,self.name), "w") as output:
            for row in self.exp_trafo_list:
                output.write(str(row)+"\n")

    def export_transformed_ply(self):
        tri_mesh_export = self.tri_mesh.copy()
        for trafomat in self.trafomat_array:
            tri_mesh_export.apply_transform(trafomat)

        tri_mesh_export.export(self.path + self.exp_path + self.name + '_transfromed.ply')

        del tri_mesh_export

    def orientate_points_with_normals(self):

        for i,value in enumerate(self.data_transformed):
            self.Vertices[i].x = value[1]
            self.Vertices[i].y = value[0] 
            self.Vertices[i].z = value[2] 

    def create_vertices ():
        pass

    def prep_orientate_mesh_kmeans (self):    
        # Get normal directions
        Normals = self.tri_mesh.vertex_normals
        self.kmeans = KMeans(n_clusters=2, random_state=0).fit(Normals)
        self.klabels = self.kmeans.labels_
        # self.export_labels(self.klabels,'Kmeans')    

    def prep_kmeans_top_bottom (self):    
        # Get normal directions
        vertices = self.vertices
        self.kmeans = KMeans(n_clusters=2, random_state=0).fit(vertices)
        self.klabels_tb = self.kmeans.labels_
        # self.export_labels(self.klabels,'Kmeans')   

# new way of orientating artefacts by using transformation matrices 
    # def transform_coordinates(self):

    #     self.data_transformed_array = np.array(self.data_transformed_array)
    #     self.data_transformed = rotate_z(self.data_transformed,3 * np.pi/2) # math.radians(np.pi))
    #     self.trafomat = rotate_z(self.trafomat, np.pi/2) # math.radians(np.pi))
        
    #     self.data_transformed_array = np.array(self.data_transformed_array)
    #     # Calculate first the side with the higher overall curvature to determine front side
    #     zero = np.sum(self.point_cloud[self.klabels == 0][:,4])/len(self.point_cloud[self.klabels == 0][:,4])
    #     one = np.sum(self.point_cloud[self.klabels == 1][:,4])/len(self.point_cloud[self.klabels == 1][:,4])
    #     if zero < one:
    #         self.data_transformed = rotate_y(self.data_transformed, math.radians(0))
    #         self.trafomat = rotate_y(self.trafomat, math.radians(0))
            
    #     elif zero > one:
    #         print('y_sign')
    #         self.data_transformed = rotate_y(self.data_transformed, np.pi)# math.radians(np.pi))
    #         self.trafomat = rotate_y(self.trafomat, np.pi)# math.radians(np.pi))            
            
    #     else:
    #         print('y?')
    #     self.data_transformed_array = np.array(self.data_transformed_array)
    #     # Determining which side is front and back
    #     z_sign_0 = np.sum(self.point_cloud[self.klabels_tb == 0][:,4])/len(self.point_cloud[self.klabels_tb == 0][:,4])
    #     z_sign_1 = np.sum(self.point_cloud[self.klabels_tb == 1][:,4])/len(self.point_cloud[self.klabels_tb == 1][:,4])

    #     if z_sign_0 < z_sign_1:
    #         self.data_transformed = rotate_x(self.data_transformed, math.radians(0))
    #         self.trafomat = rotate_x(self.trafomat, math.radians(0))
    #     elif z_sign_0 > z_sign_1:
    #         print('z_sign')
    #         self.data_transformed = rotate_x(self.data_transformed, np.pi)#  math.radians(np.pi))
    #         self.trafomat = rotate_x(self.trafomat, np.pi)# math.radians(np.pi))
    #     else:
    #         print('z?')

    #     self.trafomat = np.array(self.trafomat)

    #     for i,value in enumerate(self.data_transformed):
    #         self.Vertices[i].x = value[0]
    #         self.Vertices[i].y = value[1] 
    #         self.Vertices[i].z = value[2] 

# old function to orientate artefacts by using signs of key values ()
    # def prep_coord_exp_cloud(self):
    #     # Calculate first the side with the higher overall curvature to determine front side
    #     zero = np.sum(self.point_cloud[self.klabels == 0][:,4])/len(self.point_cloud[self.klabels == 0][:,4])
    #     one = np.sum(self.point_cloud[self.klabels == 1][:,4])/len(self.point_cloud[self.klabels == 1][:,4])

    #     # determining which side is top or bottom
    #     y_sign = np.sign(np.sum(self.data_transformed[0]))
    #     if y_sign > 0:
    #         value = rotate_y(value[0], math.radians(0))
    #     elif y_sign < 0:
    #         value = rotate_y(value[0], math.radians(180))
    #     else:
    #         print('?')

    #     if zero > one:
    #         z_sign = np.sign(np.sum(self.data_transformed[self.klabels == 0]))
    #         for i,value in enumerate(self.data_transformed):
    #             self.Vertices[i].x = value[0]
    #             self.Vertices[i].y = value[1] * y_sign
    #             self.Vertices[i].z = value[2] * z_sign
    #     elif zero < one:
    #         z_sign = np.sign(np.sum(self.data_transformed[self.klabels == 1]))
    #         for i,value in enumerate(self.data_transformed):
    #             self.Vertices[i].x = value[0]
    #             self.Vertices[i].y = value[1] * y_sign
    #             self.Vertices[i].z = value[2] * z_sign

    # def save_exp_cloud(self):
    #     # Calculate first the side with the higher overall curvature

    #     exp_cloud = [[value.x, value.y, value.z, value.quality, value.flags, 
    #                     value.red, value.green, value.blue, value.nx, value.ny, 
    #                     value.nz,value.phi, value.theta]  for value in self.Vertices.values()]

    #     self.exp_cloud = np.array (exp_cloud) 

    def export_exp_cloud_as_mesh(self):

        tuple_list = (('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('quality', 'f4'),('flags', 'f4'),
                                  ('red', 'uint8'), ('green', 'uint8'), ('blue', 'uint8'), ('nx', 'uint8'), ('ny','f4'), ('nz','f4'), ('phi','f4'), ('theta','f4'))#, ('label', 'uint8'))

        variable_list = {'x':0,'y':1,'z':2, 'quality':3, 'flags':4, 
                     'red':5, 'green':6, 'blue':7, 'nx':8, 'ny':9, 'nz':10,'phi':11, 'theta':12}

        vertices_data_types = dict((i, j) for i, j in tuple_list)

        # define 3D point cloud data
        n = self.exp_cloud.shape[0]

        # connect the proper data structures

        vertices = np.empty(n, dtype=list(tuple_list))

        for i in variable_list:

            vertices[i] = self.exp_cloud[:,variable_list[i]].astype(vertices_data_types[i])


        #vertices['label'] = klabels.astype(vertices_data_types['label'])

        faces_building = []
        # for i in range(0, num_faces):
        for value in self.Faces.values():
            faces_building.append(((list(value.indices),)))
        faces = np.array(faces_building, dtype=[("vertex_indices", "i4", (3,))])

        el_verts = PlyElement.describe(vertices, "vertex")
        el_faces = PlyElement.describe(faces, "face")


        # # save as ply
        ply_data = PlyData([el_verts, el_faces])
        ply_filename_out = self.filename + "_Kmeans_parted.ply"
        logging.debug("saving mesh to %s" % (ply_filename_out))
        ply_data.write(ply_filename_out)

    def recalculate_normals (self):

        mesh = pv.read(self.filename + "_kmeans_parted.ply")

        mesh.compute_normals(inplace=True)  # this activates the normals as well

        mesh.save(self.filename + '_kmeans_parted_normals.ply')       

    # Evaluation 
    def evaluate_trafomat(self,ev_name,ev_ending):
        print(getAngle(combine_trafomat_gm(ev_name + ev_ending)[:-1,:-1],self.trafomat[:-1,:-1]))
        print(ev_name + ev_ending)
        return getAngle(combine_trafomat_gm(ev_name + ev_ending)[:-1,:-1],self.trafomat[:-1,:-1])       

    # Oversegmentation           
    def kmeans_oversegmentation (self,depth):    
        
        time_begin = time.time()
        
        values = self.point_cloud[:,8:11]
        
        label_array = np.zeros(len(values[:,0]))
        
        self.depth = depth

        start_time = timeit.default_timer()
                
        for rep in range(1,depth):             

            index = np.arange(label_array.shape[0])[np.newaxis].T # create index array for indexing 
            
            if rep == 1:                
                array_with_indices = label_array[:][np.newaxis].T                 
            else: 
                array_with_indices = label_array[:,rep-1][np.newaxis].T                

            array_with_indices = np.concatenate((index,array_with_indices), axis=1) 
            num_rows, num_cols = array_with_indices.shape
            for count, i in enumerate (np.unique (array_with_indices[:,num_cols-1])):

                if len(values [array_with_indices[:,1] == i,]) >= 50:

                    labels = KMeans(n_clusters=2, random_state=0).fit(values [array_with_indices[:,1] == i,]).labels_                                                          
                labels_import = np.array(([str(i) + str(x + 1) for x in labels]))

                array_with_indices[array_with_indices[:,1] == i,1] = labels_import  #+ 100 + label
  
            if rep == 1:
                label_array = np.concatenate((label_array[np.newaxis].T,array_with_indices[:,1][np.newaxis].T), axis=1)
            else:
                label_array = np.concatenate((label_array,array_with_indices[:,1][np.newaxis].T), axis=1)
            self.label_array = label_array   


        end_total_time = timeit.default_timer() - start_time
        print('Time per run:', end_total_time)
        
        label_list = self.label_array[:,depth-1]
        for num,val in enumerate(np.sort(np.unique(self.label_array[:,depth-1]))):
            label_list[label_list == val] = int(num + 1)

        label_list =[int(x) for x in label_list]
        
        label_array[:,depth-1] = label_list 

        self.label_array = label_array  
        print(time.time()-time_begin)  
        np.savetxt(self.filename + '_kmeans-label.csv', label_array, delimiter=",")


