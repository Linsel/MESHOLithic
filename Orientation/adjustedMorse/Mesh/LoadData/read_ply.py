from plyfile import PlyData, PlyElement, PlyProperty, PlyListProperty
import numpy as np
from collections import Counter
import timeit

from .Datastructure import Vertex, Edge, Face

def append_value(dict_obj, key, value):
    # Check if key exist in dict or not
    if key in dict_obj:
        # Key exist in dict.
        # Check if type of value of key is list or not
        if not isinstance(dict_obj[key], list):
            # If type is not list then make it list
            dict_obj[key] = [dict_obj[key]]
        # Append the value in list
        dict_obj[key].append(value)
    else:
        # As key is not in dict,
        # so, add key-value pair
        dict_obj[key] = value


def read_ply(filename, quality_index, vertices_dict, edges_dict, faces_dict, links_dict):
    start_total_time = timeit.default_timer()
    start_time = timeit.default_timer()
    
    rawdata = PlyData.read(filename)
    vertex_properties = [p.name for p in rawdata['vertex'].properties] # get number of property position
    end_time = timeit.default_timer() - start_time
    print('Time read data file:', end_time) 
    
    
    ###############################
    # Made by Linsel
vertex_properties = [p.name for p in rawdata['vertex'].properties]

import_prop = ''

for prop in vertex_properties:
    
    import_prop = import_prop + prop +'=pt[vertex_properties.index("' + prop + '")]'
    
    
    if vertex_properties.index(prop) != len (vertex_properties)-1:
        import_prop = import_prop + ','
    else: 
        import_prop = import_prop + ',theta=np.arccos(pt[vertex_properties.index("nz")]), phi=np.arcsin(pt[vertex_properties.index("nx")]/np.cos(np.arccos(pt[vertex_properties.index("nz")])))'
    

    ##################################
    
    vals = []
    for vindex, pt in enumerate(rawdata['vertex']):
        vert = eval('Vertex(' + import_prop + ')')
        vert.fun_val = vert.quality
        vals.append(vert.fun_val)
        vertices_dict[vindex] = vert
        
    counts = Counter(vals)
    for key, value in vertices_dict.items():
        if counts[value.fun_val] > 1:
            tmp = value.fun_val
            value.fun_val = value.fun_val + (counts[value.fun_val] - 1) * 0.0000001
            counts[tmp] = counts[tmp] - 1
            
    
    eindex = 0
    unique_edges = set()
    for findex, rawface in enumerate(rawdata['face']):
        face = Face(indices=set(rawface[0]), index=findex)
        face.set_fun_val(vertices_dict)
        
        faces_dict[findex] = face
        
        for i in range(3):
            tmp = list(rawface[0])
            tmp_ind = tmp.pop(i)
            vertices_dict[tmp_ind].star["F"].append(findex)
            
            if set(tmp) not in unique_edges:
                edge = Edge(indices=set(tmp), index=eindex)
                edge.set_fun_val(vertices_dict)
                
                edges_dict[eindex] = edge
                for tmp_ed_ind in tmp:
                    vertices_dict[tmp_ed_ind].star["E"].append(eindex)
                
                eindex+=1
                
                unique_edges.add(frozenset(tmp))
    
    for edge, i  in enumerate (edges_dict):
        
    	if list(edges_dict[i].indices)[0] in links_dict:
    	     append_value(links_dict, list(edges_dict[i].indices)[0], list(edges_dict[i].indices)[1])
	
    	elif list(edges_dict[i].indices)[0] not in links_dict:

	     links_dict [list(edges_dict[i].indices)[0]] = list(edges_dict[i].indices)[1]

    	if list(edges_dict[i].indices)[1] in links_dict:

	     append_value(links_dict, list(edges_dict[i].indices)[1], list(edges_dict[i].indices)[0])
	
    	elif list(edges_dict[i].indices)[1] not in links_dict:

	     links_dict [list(edges_dict[i].indices)[1]] = list(edges_dict[i].indices)[0]   
    
                
    end_total_time = timeit.default_timer() - start_total_time
    print('Time read and prepare data:', end_total_time)
         
            


