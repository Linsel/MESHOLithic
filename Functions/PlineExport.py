from util import *


def exp_pline(  path: str,
                id: str,
                dict_mesh_info: dict,
                dict_plines: dict,
                vertices: dict,
                normals: dict):

    """
    Export of Pline data to pline file according to the GigaMesh Polyline Standard.
    """

    export_time = datetime.datetime.now()        
    exp_polyline_list = [  '# +-------------------------------------------------------------------------------+',
                                '# | PLINE file with polylines computed by the {}     |'.format(software_name),
                                '# +-------------------------------------------------------------------------------+',
                                '# | ResearchGate: https://www.researchgate.net/profile/Florian-Linsel             |',
                                '# | EMail:        florian.linsel@informatik.uni-halle.de                          |',
                                '# +-------------------------------------------------------------------------------+',
                                '# | Contact: Florian LINSEL <florian.linsel@informatik.uni-halle.de>              |',
                                '# |          eHumanities - Institute of Computer Science                          |',
                                '# |          MLU - Martin Luther University Halle-Wittenberg                      |',        
                                '# +-------------------------------------------------------------------------------+',
                                '# | Mesh:       "{}"'.format(dict_mesh_info['Mesh']),
                                '# | - Vertices: {}'.format(dict_mesh_info['Vertices']),
                                '# | - Faces:    {}'.format(dict_mesh_info['Faces']),
                                '# | Polylines:  {}'.format(dict_mesh_info['Polylines']),
                                '# | Timestamp:  ' + ' '.join([ str(export_time.strftime('%a')[:3]), 
                                                                str(export_time.strftime("%b")), 
                                                                ' ',                                                                            
                                                                str(export_time.strftime("%d")),
                                                                str(export_time.strftime("%H:%M:%S")),
                                                                str(export_time.strftime("%Y")),
                                                                str(export_time.astimezone().tzname())]),
                                '# +------------------------------------------------------------------------------------------------------------------------',
                                '# | Format: Label No. | Number of Vertices | id1 x1 y1 z1 nx1 ny1 nz1 id2 x2 y2 z2 nx2 ny2 nz2 ... idN xN yN zN nxN nyN nzN',
                                '# +------------------------------------------------------------------------------------------------------------------------']

    # iterate of polydata 
    for values in dict_plines.values(): 

        exp_polyline_list.append(' '.join([str(values['label_id']),
                                            str(values['vertices_no']),
                                            create_exp_vertices_normals(values,vertices,normals)]))

    with open(''.join([path, id, '_{}_polyline.pline'.format(software_abbreviation)]), "w") as output:
        for row in exp_polyline_list:
            output.write(str(row)+"\n")

    logging.debug('You are using the {}'.format(software_name))

def exp_pline_funcvals(path: str,
                        id: str,
                        dict_mesh_info: dict,
                        funcvals: dict,
                        var_name: str):


    """       
    Export of Pline function values as txt file according to the GigaMesh Polyline Standard.
    
    Args: 
        funcvals (dict): vertex:functionvalue dictionary, e.g. MSII curvature
        var_name (str): Name of the passed functionvalue, e.g. 'MSII'.
    
    """        

    export_time = datetime.datetime.now()

    exp_func_list = [  '# +-------------------------------------------------------------------------------+',
                            '# | PLINE file with polylines computed by the {} Software Framework        |'.format(software_name),
                            '# +-------------------------------------------------------------------------------+',
                            '# | ResearchGate: https://www.researchgate.net/profile/Florian-Linsel             |',
                            '# | EMail:        florian.linsel@informatik.uni-halle.de                          |',
                            '# +-------------------------------------------------------------------------------+',
                            '# | Contact: Florian LINSEL <florian.linsel@informatik.uni-halle.de>              |',
                            '# |          FCGL - Forensic Computational Geometry Laboratory                    |',
                            '# |          eHumanities - Institute of Computer Science                          |',
                            '# |          MLU - Martin Luther University Halle-Wittenberg                      |',        
                            '# +-------------------------------------------------------------------------------+',
                                '# | Mesh:       "{}"'.format(dict_mesh_info['Mesh']),
                                '# | - Vertices: {}'.format(dict_mesh_info['Vertices']),
                                '# | - Faces:    {}'.format(dict_mesh_info['Faces']),
                                '# | Polylines:  {}'.format(dict_mesh_info['Polylines']),
                                '# | Timestamp:  ' + ' '.join([ str(export_time.strftime('%a')[:3]), 
                                                                str(export_time.strftime("%b")), 
                                                                ' ',                                                                            
                                                                str(export_time.strftime("%d")),
                                                                str(export_time.strftime("%H:%M:%S")),
                                                                str(export_time.strftime("%Y")),
                                                                str(export_time.astimezone().tzname())]),
                            '# +-------------------------------------------------------------------------------+',
                            '# | Format: id funcval',
                            '# +-------------------------------------------------------------------------------+']

    # iterate of polydata 
    for key,value in funcvals.items(): 

        exp_func_list.append(' '.join([str(key),
                                            str(value)]))

    # for n,polyline in enumerate(self.from_pline()):
    #     self.exp_polyline_list.append(' '.join([polyline]))

    with open(''.join([path, id, '_' , '_'.join([software_abbreviation, var_name, 'funcvals.txt']) ]), "w") as output:
        for row in exp_func_list:
            output.write(str(row)+"\n")  

    logging.debug('You are using the {}'.format(software_name))

def create_exp_vertices_normals(vertices: dict,
                                normals:  dict,
                                polyline: dict) -> str:

    """
    Creates a string representation for all vertices (coordinates and normals) belonging to one polyline.

    Args:
        polyline (dict): A dictionary containing all data of a polyline.

    Returns:
        str: The string representation of vertices and normals.

    """

    exp_vertices_normals =  ' '.join(str(vertex) + 
                            ' ' + 
                            ' '.join([str(i) for i in vertices[vertex]]) +
                            ' ' + 
                            ' '.join([str(i) for i in normals[vertex]])
                            
                            for vertex in polyline['vertices'])

    return exp_vertices_normals
