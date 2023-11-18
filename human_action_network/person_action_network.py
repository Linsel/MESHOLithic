<<<<<<< HEAD
# Python3
# Generate an algorithm to get all vertices of a trimesh object
# Author: Bruno Turcksin
# Date: 2015-10-20 15:00:00.000

import dolfin as df
import numpy as np
import os
import sys

# Get the mesh
mesh = df.Mesh(sys.argv[1])

# Get the vertices
vertices = mesh.coordinates()

# Get the number of vertices
n_vertices = vertices.shape[0]

# Get the number of cells
n_cells = mesh.num_cells()

# Get the cells
cells = mesh.cells()

# Get the number of vertices per cell
n_vertices_per_cell = cells.shape[1]

# Get the number of cells per vertex
n_cells_per_vertex = np.zeros(n_vertices,dtype=np.int32)
for i in range(0,n_cells) :
  for j in range(0,n_vertices_per_cell) :
    n_cells_per_vertex[cells[i,j]] += 1

# Get the
=======
// Generate an algorithm to get all vertices of a trimesh object
function
>>>>>>> c355e9ada4b21fa8e557000d426b6f8268c0e8cc
