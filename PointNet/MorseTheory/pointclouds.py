import pandas as pd
import numpy as np
import os,sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'MorseTheory'))

from mesh import Mesh
from ply_mesh import Ply_Mesh

class point_cloud_arr(Ply_Mesh):
    def __init__(self):
        super().__init__()
        self.point_cloud = np.array([])
        self. variable_dict = {}

    def create_point_cloud(self): # point cloud for Gaussian Map
        self.point_cloud = [[value.x, value.y, value.z, value.quality,value.flags, 
                    value.red, value.green, value.blue, value.nx, value.ny, 
                    value.nz,value.phi, value.theta] for value in self.Vertices.values()]


        self.variable_dict = {'x':0,'y':1,'z':2, 'quality':3,'flags':4, 
                     'red':5, 'green':6, 'blue':7, 'nx':8, 'ny':9, 
                     'nz':10, 'phi':11, 'theta':12}


        self.point_cloud = np.array (self.point_cloud)


    def add_PCA(self,a,b):
        
        if 'PCA1' in self.variable_list:
            print ('PCA1 in pointcloud')
        else:

            X = self.point_cloud[:,a:b]


            X[np.isnan(X)] = 0

            pca = PCA(n_components=2)

            print(pca.fit(X).explained_variance_ratio_)

            principalComponents = pca.fit_transform(X)

            self.point_cloud = np.concatenate((self.point_cloud,principalComponents), axis=1) 

            self.variable_dict ['PCA1'] = 14
            self.variable_dict ['PCA2'] = 15
        
    def add_mahalanobis(self):
        if 'mahalanobis' in self.variable_dict:
            print('Mahalanobis distance exists.')
        else:
            variable_filter = ['x','y','z']

            self.variable_dict ['mahalanobis'] = 13

            mahalanobis = GM_1.MahalanobisDist(self.point_cloud,self.variable_dict,variable_filter)

            self.point_cloud = np.concatenate((point_cloud,mahalanobis), axis=1) 
    
    def calculate_stats(self): # 

        self.df_list = []
        self.df_all = []
        
        

        for num,point_col in enumerate(self.point_cloud.T):
            for key,val in self.variable_dict.items():
                
                if val == num:

                    mean = np.mean(point_col)
                    range_min = np.min(point_col)
                    q25 = np.quantile(point_col,0.25)
                    median = np.median(point_col)
                    q75 = np.quantile(point_col,0.75)
                    range_max = np.max(point_col)
                    std = np.std(point_col)
                    var = np.var(point_col)
                    
                    name = self.filename.split('/')[len(self.filename.split('/'))-1]

                    self.df_list.append([self.filename, name, key, mean, range_min, q25, median, q75, range_max, std, var])
                    for point in point_col:
                        self.df_all.append([self.filename, name, key, point])
                    
        
        self.stats = pd.DataFrame(self.df_list,columns=['filename', 'name', 'key', 'data_mean', 'data_min', 'lower_quantile','data_median','upper_quantile','data_max','data_std','data_var']) 
        self.df_data = pd.DataFrame(self.df_all, columns=['filename', 'name', 'type', 'data'])
        
    def export_stats(self):
#         self.stats = pd.DataFrame(self.df_list,columns=['key','mean', 'min', 'lower_quantile','median','upper_quantile','max','std','var']) 
#         self.df_data = pd.DataFrame(self.df_all, columns=['filename','type', 'data'])    
        self.stats.to_csv(self.filename + '_stats.csv', sep=',')
        #self.df_data.to_csv(self.filename + '_listedstats.csv', sep=',')
        
    