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


import matplotlib.pyplot as plt

import trimesh
import logging
from Classes.ObjectClasses import Mesh


# Import analyses
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans, AgglomerativeClustering
from sklearn.cluster import DBSCAN
# from scipy.spatial import cKDTree

import ot


class sinkhornVoronoi (Mesh):
    def __init__(self):
        self.time_begin = time.time()
        super().__init__()

        self.ridge_dict = None
        self.tree = None

    def load_ply(self, path, name, exp_path):
        self.path = path
        self.name = name        
        self.exp_path = exp_path
        if os.path.isdir(path + exp_path) == False:
            os.mkdir(path + exp_path)

        begin_time = time.time()
        self.tri_mesh = trimesh.load(path + name + '.ply')

        # Read the vertex data as array
        self.vertices = np.array(self.tri_mesh.vertices,dtype='float32')

        # Read the vertex data as array
        self.vertices_dict = {n:v for n,v in enumerate(self.tri_mesh.vertices)}

        # Build a KD-tree from the vertices
        self.tree = self.tri_mesh.kdtree

        print(time.time() - begin_time)

    # function to determine ridge points after segmentation
    def sample_voronoi (self,n):
      
        self.time_begin = time.time()

        self.n = n

        # cluster analyses 
        self.mini_batch_kmeans(100)
        # self.hierarchical_kmeans()
        # self.dbscan_centroids()    
        # self.    

        print(time.time()-self.time_begin)                 

        self.get_nearest_neighbor(self.centroid_mb) 

        print(time.time()-self.time_begin)       

# implemented cluster analyses

    def kmeans(self):
        
        # Run k-means clustering on the point cloud
        kmeans = KMeans(n_clusters=self.n, random_state=0).fit(self.vertices) 
        
        # Quantize the point cloud by replacing each point with its nearest cluster center
        self.quantized = kmeans.predict(self.vertices)

        # Return the quantized point cloud and the cluster centers
        self.centroids_kmeans = kmeans.cluster_centers_

    def mini_batch_kmeans(self, batch_size):
        # Create a MiniBatchKMeans object with the specified number of clusters and batch size
        kmeans = MiniBatchKMeans(n_clusters=self.n, batch_size=batch_size)

        # Fit the MiniBatchKMeans model to the point cloud
        kmeans.fit(self.vertices)

        # Get the cluster assignments for each point in the point cloud
        # labels = kmeans.predict(self.vertices)
        
        self.centroid_mb = kmeans.cluster_centers_ 
        # return labels, kmeans.cluster_centers_

    def hierarchical_kmeans(self):
        # Create an AgglomerativeClustering object with the specified number of clusters
        kmeans = AgglomerativeClustering(n_clusters=self.n)

        # Fit the AgglomerativeClustering model to the point cloud
        kmeans.fit(self.vertices)

        # Get the cluster assignments for each point in the point cloud
        labels = kmeans.labels_

        # Calculate the centroids of each cluster
        # centroids = np.zeros((self.n, self.vertices.shape[1]))
        # for i in range(self.n):
        #     centroids[i] = np.mean(self.vertices[labels == i], axis=0)

        self.centroids_h  = kmeans.cluster_centers_ # = centroids

        # return labels, centroids

    def dbscan_centroids(self):#points, eps, min_samples):
        eps = 0.1
        min_samples = 10

        # Create a DBSCAN object with the specified epsilon and minimum samples
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)

        # Fit the DBSCAN model to the point cloud
        dbscan.fit(self.vertices)

        # Get the unique cluster labels from the DBSCAN model
        labels = np.unique(dbscan.labels_)

        # Initialize an array to store the centroids of each cluster
        centroids = np.zeros((len(labels), self.vertices.shape[1]))

        # Iterate over each cluster and calculate its centroid
        for i, label in enumerate(labels):
            centroids[i] = np.mean(self.vertices[dbscan.labels_ == label], axis=0)

        self.centroids_DBscan = centroids

#
    def get_nearest_neighbor(self,centroids):
            
        # Query the tree for the nearest neighbor of the query point
        dist, index = self.tree.query(centroids)

        # Return the nearest neighbor vertex and its distance from the query point
        self.centroids_nearest_neighbor = self.vertices[index]

# plotting
    def plot_sinkhorn_dist(self):

        # Plot the two meshes and their Sinkhorn distance
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(a[:, 0], a[:, 1], a[:, 2], color='red', label='Mesh 1')
        ax.scatter(b[:, 0], b[:, 1], b[:, 2], color='blue', label='Mesh 2')
        ax.set_title('Sinkhorn distance: {:.2f}'.format(self.sinkhorn_dist))
        ax.legend()
        plt.savefig(self.path + self.exp_path + self.name + '.png')

# export centroids as pointcloud           
    def export_exp_cloud_as_mesh(self,filename ,exp_cloud,faces):

            Tuple_List = (('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('quality', 'f4'),('flags', 'f4'),
                                    ('red', 'uint8'), ('green', 'uint8'), ('blue', 'uint8'), ('nx', 'uint8'), ('ny','f4'), ('nz','f4'),('id', 'uint8'))#, ('label', 'uint8'))

            variable_list = {'x':0,'y':1,'z':2, 'quality':3, 'flags':4, 
                        'red':5, 'green':6, 'blue':7, 'nx':8, 'ny':9, 'nz':10,'id':11}

            vertices_data_types = dict((i, j) for i, j in Tuple_List)

            # define 3D point cloud data
            n = exp_cloud.shape[0]

            # connect the proper data structures

            vertices = np.empty(n, dtype=list(Tuple_List))

            for i in variable_list:

                vertices[i] = exp_cloud[:,variable_list[i]].astype(vertices_data_types[i])


            el_verts = PlyElement.describe(vertices, "vertex")

            # # save as ply
            ply_data = PlyData([el_verts])#, el_faces])
            ply_filename_out = filename + "_Kmeans_parted.ply"
            logging.debug("saving mesh to %s" % (ply_filename_out))
            ply_data.write(ply_filename_out)

# calculate the sinkhorn distance
def calc_sinkhorn_dist(a,b,n):

    # Compute the cost matrix between each pair of points in the two meshes
    C = np.sum((a[:, None, :] - b[None, :, :]) ** 2, axis=-1)

    # Compute the Sinkhorn distance
    reg = 1e-3
    G0 = ot.emd(np.ones(n) / n, np.ones(n) / n, C, reg)
    sinkhorn_dist = np.sum(G0 * C)
    return sinkhorn_dist
    # self.plot_sinkhorn_dist()