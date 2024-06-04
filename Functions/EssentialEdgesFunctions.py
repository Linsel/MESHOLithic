from util import *
from Classes.BasicClasses import manualEdges

def get_manual_edges(path, id):

    """
    imports and returns edges files and differentiate between edges, which are referenced to 3D mesh or need to be referenced to the 
    segmentation label. 
    
    Args:
        path (str): path to the file.
        id (str): id of the referenced node or edge file.

    Returns:
        manual_edges (set): returns set of edges or referenced edges
    """

    mE = manualEdges()

    try:
        mE.import_edges_nodes(path, id)
        print ('Has edges and nodes files')     
        manual_edges = mE.manual_edges            
        
        return manual_edges     
       
    except:

        try:
            mE.import_edges(path, id)
            print ('Has edges file')  
            manual_edges = mE.manual_edges               
        
            return manual_edges 
                  
        except:
            print ('Has no edge file')


def get_manual_links(linkfilepath):

    """
    imports and returns edges files and differentiate between edges, which are referenced to 3D mesh or need to be referenced to the 
    segmentation label. 
    
    Args:
        get_manual_links (str): path to the file.

    Returns:
        manual_edges (set): returns set of edges or referenced edges
    """

    edge_df = pd.read_csv(linkfilepath,
                            sep=',',header=0)

    
    manual_edges  = {(int(edge[0]),int(edge[1])) for _,edge in edge_df.iterrows()}

    return manual_edges

def export_links (links,*args):

    write_links_txt_file (links, ''.join (['_'.join([arg for arg in args]),
                                            '_links'
                                            ]))
    
def export_links_eval (link_dict,*args):

    write_links_txt_file (link_dict, ''.join (['_'.join([arg for arg in args]),
                                            '_eval_links'
                                            ]))
            