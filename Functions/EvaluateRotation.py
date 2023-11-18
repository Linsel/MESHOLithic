import pandas as pd 
import numpy as np

# combine multiply transformation matrices from one file (GM)
# def combine_trafomat_GM (filename):
#     df = pd.read_csv(filename,delimiter='###',header=None,engine='python')[0]
#     np_out = np.empty((0,4), float)
#     for row in df:
#         if row[0] != "#":
#             if ',' in row:
#                 row = row.replace(',','.')
#             data = np.array([float(x) for x in row.split(' ')],ndmin=2)
#             np_out = np.append(np_out,np.array(data),axis=0)     
#         trans_mat = np.array(np_out[:4, :])
#     for index, values in np.ndenumerate(np_out[:,0]):
#         if(index[0] % 4 == 0):        
#             trans_ind = index[0] 
#             trans_mat = np.matmul(trans_mat,np_out[trans_ind:trans_ind+4, :])

#     return trans_mat

def combine_trafomat_gm (filename):
    df = pd.read_csv(filename,delimiter='###',header=None,engine='python')[0]
    np_out = np.empty((0,4), float)
    for row in df:
        if row[0] != "#":
            if ',' in row:
                row = row.replace(',','.')
            data = np.array([float(x) for x in row.split(' ')],ndmin=2)
            np_out = np.append(np_out,np.array(data),axis=0)     
    for index, values in np.ndenumerate(np_out[:,0]):
        if(index[0] % 4 == 0):        
            trans_ind = index[0] 
            if 'trans_mat' not in locals():
                trans_mat = np_out[trans_ind:trans_ind+4, :]
            else:
                trans_mat = np.matmul(trans_mat,np_out[trans_ind:trans_ind+4, :])
    return trans_mat

# Calculate angle between two transformation matrices using quaternions
# 
def get_angle(P, Q):
    R = np.dot(P, Q.T)
    theta = (np.trace(R)-1)/2
    return np.arccos(theta) * (180/np.pi)

def get_theta_rotmat(P, Q):
    R = np.dot(P, Q.T)
    theta = (np.trace(R)-1)/2
    return theta

def get_theta_vectors (v1, v2):
    """Calculate the angle between two vectors from the same origin on a unit sphere."""
    
    # Calculate the dot product of the two vectors
    dot_product = np.dot(v1, v2)
    
    # Calculate the angle between the two vectors using the dot product
    theta = np.arccos(dot_product)

    return theta    

def compare_angle(P,Q):
    """ comment cos between vectors or matrices """
    p_flat = P.reshape(-1)  # views
    q_flat = Q.reshape(-1)
    return (np.dot(p_flat, q_flat)/ max(norm(p_flat) * norm(q_flat), 1e-10))
