import numpy as np
import trimesh

# generates a unitarrow for plotting 3D edges of directed graph models
# remark: arrow mesh is not a unitarrow  
def generate_unitarrow():
    length = 0.9
    radius = 0.1    

    arrow_length = length * (2/3) 
    arrow_radius = radius    
    arrow_correction = 0.1 

    arrow_head_length = length - arrow_length
    arrow_head_radius = radius * 3   
    arrow_head_correction = arrow_correction / 2 

    # Generate the arrow body as a cylinder
    cylinder = trimesh.creation.cylinder(radius=arrow_radius, 
                                         height=arrow_length)
    
    # Calculate the translation vector to position the arrow body
    translation_arrow1 = np.array([0, 0, (arrow_length + arrow_correction) / 2])

    cylinder.apply_translation(translation_arrow1)

    # Generate the arrow head as a cone
    cone = trimesh.creation.cone(radius=arrow_head_radius, 
                                 height=arrow_head_length)
    
    # Calculate the translation vector to position the arrow head
    translation_arrow2 = np.array([0, 0, arrow_length + arrow_head_correction])    

    # Translate the cone to the correct position
    cone.apply_translation(translation_arrow2)

    # Combine the body and head to form the arrow geometry
    arrow_geometry = trimesh.util.concatenate(cylinder, cone)

    arrow_mesh = trimesh.Trimesh(vertices=arrow_geometry.vertices, 
                                 faces=arrow_geometry.faces)

    return arrow_mesh

# generates a unitconnection for plotting 3D edges of directed graph models
# remark: cylinder mesh is not a unitcylinder  
def generate_unitconnection():

    length = 0.9
    radius = 0.1

    # Generate the arrow body as a cylinder
    cylinder = trimesh.creation.cylinder(radius=radius, 
                                         height=length)
    
    # Calculate the translation vector to position the arrow body
    translation_cylinder = np.array([0, 0, (length + 0.1 )/2])

    cylinder.apply_translation(translation_cylinder)

    return cylinder



