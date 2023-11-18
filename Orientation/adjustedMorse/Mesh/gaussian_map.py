from mesh import Mesh
from LoadData.Datastructure import Vertex, Edge, Face
from LoadData.read_ply import read_ply


from PlotData.write_overlay_ply_file import write_overlay_ply_file
from PlotData.write_labeled_cells_overlay import write_cells_overlay_ply_file

import timeit
import os
import numpy as np

class Gaussian_Map (Mesh):
    
    def init (self):
        super(self).__init__()

    def load_vertices_normals_ply(self, filename, quality_index):
        read_ply(filename, quality_index, self.Vertices, self.Edges, self.Faces, self.Links)
        self.filename = os.path.splitext(filename)[0]