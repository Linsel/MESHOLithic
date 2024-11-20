import os,sys

currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from scipy import stats


from util import *

from minions.DataMinions import *
from minions.FolderMinions import get_file_paths_filtered,get_file_paths_subfolders
from minions.LabelMinions import label_import
from minions.EdgeMinions import *




from Functions.EssentialEdgesFunctions import get_manual_edges, get_manual_links

from Functions.exportFiles.writeTxt import write_funvals_txt_file
from Functions.exportFiles.writeJson import write_dictionary_w_indent_json
from Functions.EvaluateGraph import evaluate_directed_edges,directed_edges_parameters

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
    linkfilepath  = kwargs["linkfilepath"]
    graphfilepath  = kwargs["graphfilepath"]
    single_vec_list = kwargs["single_vec_list"]

    id = kwargs ['id'].split('_')[0]

    funcs = {
            'mean':np.mean,
             'median':np.median,
             'std':np.std#,
            #  'argmax':np.argmax,
            #  'argmin':np.argmin,
            #  'hmean': stats.gmean
             }

    
    # edges_path = get_file_paths_filtered(**{'path':path,'folder':folder,'filename':linkname})

    # graphs = get_file_paths_filtered(**{'path':path,'folder':folder,'filename':graphname})

    # acc_edges = {}

    # filepath = graphs [id]

    # for file,filepath in graphs.items():
        
    acc_edges = {id:{}}
    # print(edges_path [id])

    edges = get_manual_links (linkfilepath)

    with open(graphfilepath) as handle:
        G_edges = json.loads(handle.read())

    # edges = get_manual_edges(edges_path [id][:-len('links.csv')], '')
    # G_json = ''.join ([subfolder_path,file])
    # with open(filepath) as handle:
    #     G_edges = json.loads(handle.read())

    file_paths = {}

    for filename in single_vec_list:
        file_paths_all = get_file_paths_filtered (**{'path':path,'folder':folder,'filename':filename})
        file_paths.update({filename:file_paths_all[id]})

    # file_ncols contains the number of columns per imported file 
    df,file_ncols = merge_data_simple(file_paths)

    df.columns = [n+1 for n,_ in enumerate(df.columns)]
            
    # calculates the mean value of all parameters per node of all edges
    edge_params = {func_name:{k:{c:func([df[c][n] if n in df[c].index else 0 for n in vals['nodes']]) for c in df.columns} for k,vals in G_edges.items() } for func_name,func in funcs.items() }

    # import updated border labels
    border_path = get_file_paths_filtered(**{'path':path,'folder':folder,'filename':f'updated-labels-bt{border_thickness}.txt'})[id][0]

    # break
    
    borders = label_import(border_path)

    for n,c in enumerate(df.columns):
        acc_edges [id][n] = {}

        for func_name,edge_param in edge_params.items():
            acc_edges [id][n][func_name] = {}

            edge_param_border = {}
            for k,val in borders.items():

                if str(val) in edge_param.keys():
                    edge_param_border.update({k:float(np.format_float_positional(edge_param[str(val)][c]))})
                # elif np.nan in np.format_float_positional(edge_param[str(val)][c]):
                #     print(edge_param[str(val)][c])
                #     edge_param_border.update({k:0})
                elif np.isnan(edge_param[str(val)][c]):
                    edge_param_border.update({k:0})

                else:
                    edge_param_border.update({k:0})

            edge_param_vals = {tuple(G_edges[str(val)] ['edge']):np.float32(np.format_float_positional(edge_param[str(val)][c])) if str(val) in edge_param.keys() else 0 for k,val in borders.items()}  

            
            # for p in edge_param_vals.values():
            #     if np.isnan(p):
            #         print(c,func_name,[p for p in edge_param_border.values()])
            #         continue     

                
            # assigns mean value of regarded vertices to all vertices in bordering parts
            # edge_param_border = {k:np.format_float_positional(edge_param[str(val)][c]) for k,val in borders.items() } 
            filename = f"{id}_{file_ncols[n+1][:-4]}_{str(n)}-{func_name}.txt"  
            edge_param_vals_path =  f"{path}{folder}/{subfolder}/"  # [:-5]]) 

            write_funvals_txt_file (edge_param_border, edge_param_vals_path,filename)   
                
            edge_set = set(edge_param_vals.keys())

            ridge_pairs = get_ridge_pairs(edge_set,edge_param_vals)

            directed_edges_dict = get_directed_edges(ridge_pairs)

            directed_edges = {edge for edge in directed_edges_dict.keys() if edge in edges or (edge[1],edge[0]) in edges}
            directed_edges_rev = {(k[1],k[0]) for k in directed_edges}
            
            # directed_edges_simp = {edge for edge in directed_edges if edge in simp_edges or  (edge[1],edge[0]) in simp_edges}     
            # directed_edges_simp_rev = {(k[1],k[0]) for k in directed_edges_simp}       
            
            acc_edges [id][n][func_name].update({'E':evaluate_directed_edges(directed_edges,edges)})
            acc_edges [id][n][func_name].update({'E_rev':evaluate_directed_edges(directed_edges_rev,edges)})
            # # print("Edge:",acc_edges ['E'][n][1]) 

    single_vec_list_names = '-'.join ([i[:-4] for i in single_vec_list])

    single_vec_list_names = get_matching_splits (single_vec_list)

    filepath = f'{path}/{folder}/{subfolder}/{id}_{single_vec_list_names}_edge-eval.json'
    print('done')
    write_dictionary_w_indent_json (filepath,acc_edges,4)
        
    # for filen, acc_edge in acc_edges.items():
    #     print(filen)
    #     for func_name, accs in acc_edge.items():
    #         print(func_name)
    #         print_accuracy_edges(accs)
        

def node_value_evaluation_procedure (obj,**kwargs):

    path = kwargs["path"]
    folder = kwargs["folder"]
    linkname  = kwargs["linkname"]
    param_ext  = kwargs["param_ext"]

    id = kwargs ['id'].split('_')[0]

    funcs = {
            'mean':np.mean,
             'median':np.median,
             'std':np.std#,
            #  'argmax':np.argmax,
            #  'argmin':np.argmin,
            #  'hmean': stats.gmean
             }

    node_param_paths = get_file_paths_filtered(**{'path':path,'folder':folder,'filename':param_ext})

    acc_edges = {}

    filepath = node_param_paths [id]

    with open(filepath) as handle:
        para = json.loads(handle.read())


    edges_path = get_file_paths_filtered(**{'path':path,'folder':folder,'filename':linkname})
    # for file,filepath in graphs.items():
        
    acc_edges [id] = {}

    edges = get_manual_edges(edges_path [id][:-len(linkname)], '')

    para_name = param_ext.split('.')[0]

    exp_path = '/'.join(['path,folder,subfolder'])

    directed_edges_parameters (exp_path,id,edges,para,para_name)


def xlsx_to_csv_sheets_procedure (obj,**kwargs):

    path = kwargs ['path']
    folder = kwargs ['folder']
    subfolder = kwargs["subfolder"]    
    filename = kwargs ['filename']

    filepath = f'{path}/{folder}/{subfolder}/{filename}.xlsx'


    # Load the Excel file
    excel_data = pd.ExcelFile(filepath)

    # Iterate over each sheet
    for sheet_name in excel_data.sheet_names:
        # Read the sheet into a DataFrame
        df = pd.read_excel(filepath, sheet_name=sheet_name)

        sheet_name = sheet_name.replace('.','-')
        sheet_name = sheet_name.replace('"','')
        
        # Create a CSV file name based on the sheet name
        csv_file = f"{path}/{folder}/{subfolder}/{filename}{sheet_name}_nodes.csv"
        
        # Save the DataFrame to a CSV file
        df.to_csv(csv_file, index=False)
