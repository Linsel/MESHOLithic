import os,sys

currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from util import *

from minions.DataMinions import *
from minions.FolderMinions import get_file_paths_filtered,get_file_paths_subfolders
from minions.LabelMinions import label_import
from minions.EdgeMinions import *


from Functions.EssentialEdgesFunctions import get_manual_edges

from Functions.exportFiles.writeTxt import write_funvals_txt_file
from Functions.EvaluateGraph import evaluate_directed_edges

def merge_data_procedure (obj,**kwargs):

    path = kwargs ['path']
    folder = kwargs ['folder']
    endings  = kwargs['endings']
    skip  = kwargs['skip']
    
    meta_files = get_ply_metadata (path,folder,endings)

    for name,files in meta_files.items():

        extracted_data = extract_data_ply_metadata(folder,name,files)

        kwargs.update(extracted_data) 

        try:
            max_step =  [int(file_split.split('_')[-2]) for file in files for file_split in file.split('/') if file_split.startswith(''.join([folder, '_'])) ][0]

        except:
            
            print (name)
            continue


        # files_folders = {file_split.split('_')[-1]:[f for f in files for f_split in f.split('/') if f_split.split('_')[-1] == file_split.split('_')[-1]] for file in files for file_split in file.split('/') if file_split.startswith(''.join([folder, '_']))}
        file_folders = list({file_split.split('_')[-1] for file in files for file_split in file.split('/') if file_split.startswith(''.join([folder, '_']))})

        new_folder = '_'.join([folder,'{:0>2}'.format(max_step+1), 'MAT'])

        if not new_folder in os.listdir('/'.join([path,folder])):

            os.mkdir('/'.join([path,folder,new_folder]))

        df = merge_data (path,folder,new_folder,name,file_folders,files,skip) 

    return df,files


def single_value_evaluation_procedure (obj,**kwargs):

    path = kwargs["path"]
    folder = kwargs["folder"]
    subfolder = kwargs["subfolder"]
    border_thickness = kwargs["border_thickness"]
    links_ext  = kwargs["links_ext"]
    graph_ext  = kwargs["graph_ext"]
    single_vec_list = kwargs["single_vec_list"]

    edges_path = get_file_paths_filtered(**{'path':path,'folder':folder,'filename':links_ext})

    graphs = get_file_paths_filtered(**{'path':path,'folder':folder,'filename':graph_ext})

    for file,filepath in graphs.items():
        
        acc_edges = {'E':{},
                        'E_rev':{}}
        
        edges = get_manual_edges(edges_path [file][:-len(links_ext)], '')

        # if simp_edges == None:
        #     break

        # G_json = ''.join ([subfolder_path,file])

        with open(filepath) as handle:
            G_edges = json.loads(handle.read())

        file_paths = {filename:list(get_file_paths_filtered (**{'path':path,'folder':folder,'filename':filename}).values())[0] for filename in single_vec_list}

        # file_ncols contains the number of columns per imported file 
        df,file_ncols = merge_data_simple(file_paths)
        print(file_ncols)

        df.columns = [n+1 for n,_ in enumerate(df.columns)]
                
        # calculates the mean value of all parameters per node of all edges
        edge_mean = {k:{c:np.mean ([df[c][n] if n in df[c].index else 0 for n in vals['nodes']], dtype = np.float32) for c in df.columns[1:]} for k,vals in G_edges.items()}

        # import updated border labels
        border_path = list(get_file_paths_filtered(**{'path':path,'folder':folder,'filename':f'updated-labels-bt{border_thickness}.txt'}).values())[0]
        borders = label_import(border_path)

        for n,c in enumerate(df.columns[1:]):

            # assigns mean value of regarded vertices to all vertices in bordering parts
            edge_mean_border = {k:np.format_float_positional(edge_mean[str(val)][c]) for k,val in borders.items()} 
            filename = f"{file}_{file_ncols[n+1][:-4]}-{str(n+1)}.txt"  
            edge_mean_vals_path =  f"{path}{folder}/{subfolder}/"  # [:-5]]) 

            write_funvals_txt_file (edge_mean_border, edge_mean_vals_path,filename)   

            edge_mean_vals = {tuple(G_edges[str(val)] ['edge']):np.float32(np.format_float_positional(edge_mean[str(val)][c])) for k,val in borders.items()}   

            edge_set = set(edge_mean_vals.keys())

            ridge_pairs = get_ridge_pairs(edge_set,edge_mean_vals)

            directed_edges_dict = get_directed_edges(ridge_pairs)

            directed_edges = {edge for edge in directed_edges_dict.keys() if edge in edges or (edge[1],edge[0]) in edges}
            directed_edges_rev = {(k[1],k[0]) for k in directed_edges}
            
            # directed_edges_simp = {edge for edge in directed_edges if edge in simp_edges or  (edge[1],edge[0]) in simp_edges}     
            # directed_edges_simp_rev = {(k[1],k[0]) for k in directed_edges_simp}       
            
            acc_edges ['E'].update({n:evaluate_directed_edges(directed_edges,edges)})
            # print("Edge:",acc_edges ['E'][n][1])

            acc_edges ['E_rev'].update({n:evaluate_directed_edges(directed_edges_rev,edges)})
            # print("Edge Rev:",acc_edges ['E_rev'][n][1])           

            # acc_edges ['E_simp'].update({n:evaluate_directed_edges(directed_edges_simp,simp_edges)}) 
            # # print("Edge Simp:",acc_edges['E_simp'][n][1])

            # acc_edges ['E_simp_rev'].update({n:evaluate_directed_edges(directed_edges_simp_rev,simp_edges)})
            # # print("Edge Simp Rev:",acc_edges['E_simp_rev'][n][1])            
