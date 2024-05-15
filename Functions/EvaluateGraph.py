from Functions.exportFiles.writeTxt import write_links_csv_file, write_links_eval_csv_file
import json

# compare two directed edge sets 
def evaluate_directed_edges (GT,RES):

    """
    Determines the rightly and wrongly determined directions of directed edges.

    Parameters
    ------------
    GT: set 
        Ground truth set, which is considered to be true.
    RES: set 
        Result set of edges which get compared to GT set.

    Returns
    ------------

    eval_edge_direction: dict
        Dictionary of edges, which are either be correctly (1) or incorrectly (0) directed 

    accuracy: float
        Accuracy of RES edges (1) 

    """

    # dictionary of edges, which are either be correctly (1) or incorrectly (0) directed
    eval_edge_direction = {edge:(1 if edge in RES else 0) for edge in GT}

    # count of correctly directed edges (1) 
    eval_para_sum = sum([val for val in eval_edge_direction.values() if val == 1])
    # count of incorrectly directed edges (1)     
    eval2_para_sum = sum([1 for val in eval_edge_direction.values() if val == 0])

    # accuracy of RES edges (1) 
    accuracy = sum([val for val in eval_edge_direction.values() if val == 1])/ (eval_para_sum + eval2_para_sum)

    # print('Right positve {}, Wrong negative: {}; Ratio: {}'.format(eval_para_sum,eval2_para_sum,accuracy))    

    return eval_edge_direction, accuracy

def less_equal_greater (edges,para,case):

    if case == 'less':
        return {edge
                    if para [edge[0]] < para [edge[1]] 
                    else 
                (edge[1],edge[0])

                for edge in edges}
    
    if case == 'equal':
        return {edge
                    if para [edge[0]] == para [edge[1]] 
                    else 
                (edge[1],edge[0])

                for edge in edges}
    
    if case == 'greater':
        return {edge
                    if para [edge[0]] > para [edge[1]] 
                    else
                (edge[1],edge[0])

                for edge in edges}

def export_links (links,*args):
    print(args)

    write_links_csv_file (links, ''.join ([args[0],
                                           ''.join([arg for arg in args[1:]]),
                                            '_links'
                                            ]))
    
def export_links_eval (eval,*args):

    write_links_eval_csv_file (eval, ''.join ([args[0],
                                               ''.join([arg for arg in args[1:]]),
                                                '_eval_links'
                                            ]))
                                                                                                         
def directed_edges_parameters (path,id,edges,para,para_name):

    cases = ['less','equal','greater']

    # compare_edges = {case:less_equal_greater (edges,para,case) for case in cases}

    eval_edge_directions = {}

    print(para_name,':')

    for case in cases:

        print(para_name,'({})'.format(case),':')

        compare_edges = less_equal_greater (edges,para,case) 
        
        edge_direction, accuracy = evaluate_directed_edges (edges, compare_edges)
 
        args = [path,id,para_name,case,'acc-{}'.format(str(round(accuracy,2)))]

        export_links (compare_edges,*args)

        export_links_eval (edge_direction,*args)


def direct_edges_w_parameter (path,id,preprocessed,edges,para,para_name):

    cases = ['less','equal','greater']

    for case in cases:

        print(para_name,'({})'.format(case),':')

        compare_edges = less_equal_greater (edges,para,case) 
 
        args = [path,id,preprocessed,para_name,'_',case]

        export_links (compare_edges,*args)

def direct_edges_w_phase (path,id,preprocessed,edges,para,para_name):

    case = 'less'

    compare_edges = less_equal_greater (edges,para,case) 

    args = [path,id,preprocessed,para_name]

    export_links (compare_edges,*args)

def export_graphs_json(G, fname):
    
    json.dump(dict(nodes=[[n, G.node[n]] for n in G.nodes()],
                   edges=[[u, v, G.edge[u][v]] for u,v in G.edges()]),
              open(fname, 'w'), indent=3)
    


