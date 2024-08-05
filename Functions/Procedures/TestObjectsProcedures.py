import meta_util
import networkx as nx

from minions.PlineMinions import plot_linegraph_attribute

def polyline_MSII_procedure (obj,**kwargs):

    path = kwargs['path']
    ind = kwargs['ind']
    radius = kwargs['radius']
    nrad = kwargs['nrad']


    # creating the polyline test object
    obj.preparing(path,ind)
    obj.create_testpolyline()
    # obj.testpolyline.plot_polyline_simple()

    obj.testpolyline.create_basic_info()
    obj.testpolyline.create_pline()    

    # p = TO.testpolyline.pline 
    # p.nrad,p.maxrad = n_rad,radius    

    obj.testpolyline.pline.calc_II_new_sphere (radius,nrad)
    obj.testpolyline.pline.get_feature_vectors()

    title = f'MSII-1D'

    for rad in obj.testpolyline.pline.radii:

        obj.testpolyline.pline.select_radius_angle(rad)

        nx.set_node_attributes(obj.testpolyline.G, obj.testpolyline.pline.dict_radius_selected_angle, rad)
        exp_path = '{path}{ind}{title}{rad}.png'

        plot_linegraph_attribute(obj.testpolyline.G,rad,title,f'Radius: {rad}', exp_path)



