class Vertex:
    def __init__(self, x=None, y=None, z=None,
                quality=None, flags=None, red=None, 
                green=None, blue=None, index=None,
                nx=None,ny=None, nz=None,
                theta=None,phi=None, fun_val=None):
        
        self.index = index
        self.x = x
        self.y = y
        self.z = z
        self.quality = quality
        self.flags = flags
        self.red = red
        self.green = green
        self.blue = blue
        self.nx=nx
        self.ny=ny 
        self.nz=nz
        self.theta=theta
        self.phi=phi
        
        self.fun_val = fun_val        
        self.star = {}
        self.star["F"] = []
        self.star["E"] = []
        
        
    def __str__(self):
        return str(self.index)

# indices will be read in as sets
class Edge:
    def __init__(self, indices=None, fun_val=None, index=None):
        self.indices = indices
        self.fun_val = fun_val

        self.index = index
        
    def set_fun_val(self, vertices_dict):
        self.fun_val = []
        for ind in self.indices:
            self.fun_val.append(vertices_dict[ind].fun_val)
        self.fun_val.sort(reverse=True)
        
    def __str__(self):
        return str(self.indices)


# indices will be read in as sets
class Face:
    def __init__(self, indices=None, fun_val=None, index=None):
        self.indices = indices
        self.fun_val = fun_val

        self.index = index
        
    def set_fun_val(self, vertices_dict):
        self.fun_val = []
        for ind in self.indices:
            self.fun_val.append(vertices_dict[ind].fun_val)
        self.fun_val.sort(reverse=True)
        
        
    def __str__(self):
        return str(self.indices)

# class Labels:
#     def __init__(self, indices=None, index=None, label=None):
#         self.indices = indices

#         self.index = index
#         self.label = label
        
#     def __str__(self):
#         return str(self.indices)
    

    

class Cell:
    
    def __init__(self, label):
        self.label = label
        
        self.vertices = set()
        self.boundary = set()
        
        self.neighbors = {}
        
        self.neighborlist = []
