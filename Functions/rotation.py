import math
import numpy as np


def rotate_x(v, angle):
    t = get_rotate_x(angle)
    return [matrix_vector_multiply(t, vi) for vi in v]

def rotate_y(v, angle):
    t = get_rotate_y(angle)
    return [matrix_vector_multiply(t, vi) for vi in v]

def rotate_z(v, angle):
    t = get_rotate_z(angle)
    return [matrix_vector_multiply(t, vi) for vi in v]

def get_rotate_x(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    t = [[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]]
    return t

def get_rotate_y(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    t = [[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]]
    return t

def get_rotate_z(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    t = [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    return t

def flip_yz(v):
    t = [[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    return [matrix_vector_multiply(t, vi) for vi in v]

def flip_xz(v):
    t = [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    return [matrix_vector_multiply(t, vi) for vi in v]

def flip_xy(v):
    t = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]]
    return [matrix_vector_multiply(t, vi) for vi in v]        

def matrix_vector_multiply(m, v):
    return [sum(vi * mij for vi, mij in zip(v, row)) for row in m]
 
def get_flip_xz():
    t = [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    return t

def has_axis_flip(matrix):
    determinant = np.linalg.det(matrix)
    return determinant == -1

