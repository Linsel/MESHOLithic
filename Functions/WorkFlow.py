import os,sys,json
import pandas as pd
from minions.FolderMinions import *

# currentdir = os.getcwd()
# parentdir = os.path.dirname(currentdir)
# sys.path.insert(0, currentdir) 
# sys.path.insert(0, parentdir) 

from Functions.main import procedures

def export_workflow (path, 
                     folder, 
                     workflow,
                     step):    
    
    workflow_path = "/".join([path,
                              folder,
                              ''.join(['workflow-',
                                       '-'.join(step),
                                       '.json'])
                              ])

    # workflow export 

    with open(workflow_path,"w") as f:
        json.dump(workflow,f)

def run_workflow (path:str, 
                  folder:str, 
                  workflow:dict):
    """
    Function to run multitude of processes from including GigaMesh functions and derivative from 3D meshes. 

    Args:
        path (str): path to root folder of projects.
        folder (str): directory of selected project.
        workflow (dict): nested dictionary, which includes numbered steps with a key value pair of id:step. 
                        step includes all parameters needed for one processing routine:

                            'name': directory name of the process, in which will the resulting data will be stored. 
                            'derived_from': ending of the folder, which specifies the directory, from which the new data is derived from.        

                            'class': all processes are assigned to one processing class.  
                            'method': name of the process.

                            'metadata': list of file ending sored in a 'metadata' subdirectory.
                            'variables': dictionary with all parameters needed for the process, which can vary between processes.
    """
    

    
    steps = [v['name'] for v in workflow.values()]

    export_workflow(path, folder, workflow, steps)

    for step in workflow.values():      

        paths_subfolders = get_file_paths_subfolders (path, folder)
        
        dir_dict = create_directory_dictionary ('/'.join([path,folder]))
        last_step = max([int(key.split('_')[-2]) for key in dir_dict.keys()])

        for ind,processes in paths_subfolders.items():

            missing_files = []            
            
            try:
                if ind == '':
                    continue
                ply_file = [file for process, files in processes.items() for file in files if step['derived_from'] == process and file.endswith('.ply')][0]

            except:
                continue

            print("The processing step {} starts".format(step['name']))

            files_preprocesses =  {process for values in paths_subfolders.values() for process in values.keys()}

            if step['name'] in files_preprocesses:
                print('All processes of ',step['name'], 'were already created.')
                continue            

            if len(missing_files) > 0:
                break
            else:
                print(ind)

            filepaths = {}

            # defining list of secondary datasets needed to proceed with the procedure
            secondary_data = {'linkname':'linkfilepath','labelname':'labelfilepath','nodesname':'nodefilepath'}

            for name,filepath in secondary_data.items():

                if name in step['variables'].keys():      
                    filepaths [filepath] = error_missing_data_multiple (ind,processes,files_preprocesses, step['variables'],name)
                    
                    # if filepath not in filepaths.keys():    
                    #     print(2)
                    #     filepaths [filepath] = error_missing_data_multiple (ind,processes,files_preprocesses, step['variables'],name)  

                    # elif filepaths [filepath] == None:
                    #     print(2.2)
                    #     filepaths [filepath] = error_missing_data_multiple (ind,processes,files_preprocesses, step['variables'],name)
                else:
                    continue

                if filepath not in filepaths.keys():
                    continue

                if filepaths [filepath] == None:
                    missing_files.append([filepath])
                    continue                    

            print('All required datasets are available and the process is continuing.')   

            if 'subfolder' not in step['variables'].keys():
                subfolder = ply_file.split('/')[-2]

            elif 'subfolder' in step['variables'].keys():
                subfolder = step['variables']['subfolder']

            folder_path = '/'.join(['/'.join(ply_file.split('/')[:-1]),''])


            file = ply_file.split('/')[-1][:-4]

            temp_kwargs = { 'path':folder_path,
                        'id':file,
                        'class':step['class'],
                        'method':step['method'],
                        'subfolder':subfolder}
            
            if 'parameters' in step['variables'].keys():
                temp_kwargs['parameters'] = step['variables']['parameters']

            temp_kwargs.update (filepaths)

            if 'nodesname' in step['variables'].keys():
                df = pd.read_csv (temp_kwargs['nodefilepath'],sep=",")

                values_dict = {row['gt_label']:row['phase'] for _, row in df.iterrows()}

                params = {'name':'', 'values':values_dict}

                temp_kwargs['params'] = params                    

            temp_kwargs.update(step['variables'])

            procedures (**temp_kwargs)

        if len(missing_files) > 0:

            print ("Unfortunately, some files (including {}) needed to terminate all processes for {} are missing.".format(', '.join(missing_files[:2]), ind))

        elif 'subfolder' not in locals():
            continue

        else:

            folder_dict = { step['derived_from']:[file  
                                                        for processes in paths_subfolders.values() 
                                                            for process,files in processes.items() 
                                                                for file in files if process == step['derived_from']]
                            }
            
            move_resulting_files(path,folder,subfolder,step,folder_dict,last_step)

        


# old code 


# def run_workflow (path, 
#                   folder, 
#                   workflow):

#     last_step = get_last_step (path,folder,workflow)
    
#     steps = [v['name'] for v in workflow.values()]
#     max_steps = max([v['stage'] for v in workflow.values()])

#     export_workflow(path, folder, workflow, steps)

#     for n in range(last_step[0],max_steps):

#         workflow_step (path,folder,workflow,n)


# def workflow_step (path,folder,workflow,n):

#     next_step = n + 1

#     newfolder = '_'.join([  folder,
#                             str("{:02d}".format(workflow[n]['stage'])),
#                             workflow[n]['name']])

#     folder_path = '/'.join([path,
#                             folder,
#                             newfolder,
#                             ''])

#     files = os.listdir(folder_path)


#     if workflow[next_step]['add_labels'] == True:

#         kwargs = {
#             'path':path, 
#             'folder':folder,
#             'newfolder':newfolder,
#             'filename':workflow[next_step]['labelname']}
        
#         # add_labels(**kwargs)
#         label_paths = get_file_paths_filtered(**kwargs)
        

#     if workflow[next_step]['add_links'] == True:

#         kwargs = {
#             'path':path, 
#             'folder':folder,
#             'newfolder':newfolder,
#             'filename':workflow[next_step]['linkname']}  
                        
#         # add_links(**kwargs)
#         link_paths = get_file_paths_filtered(**kwargs)
                

#     for file in files:
#         # try:
#         print ("Begin to process {}".format(file))
#         if file.endswith('ply'):

#             temp_kwargs = { 'path':folder_path,
#                             'id':file[:-4],
#                             'class':workflow[next_step]['class'],
#                             'method':workflow[next_step]['method'],
#                             'parameters': workflow[next_step]['parameters']}
            
#             temp_kwargs.update(workflow[next_step]['variables'])

#             if workflow[next_step]['add_labels'] == True:

#                 print(label_paths)

#                 temp_kwargs['labelfilepath'] = label_paths[file.split('_')[0]]
                

#             if workflow[next_step]['add_links'] == True:

#                 print(link_paths)

#                 temp_kwargs['linkfilepath'] = link_paths [file.split('_')[0]] 
       

#             procedures (**temp_kwargs)

#         # except: 
#             # print ("Something went wrong while calculating {}".format(file))
#             # continue
                
#     if workflow[next_step]['method'] != '':

#         newfolder = str("{}_{}_{}".format(  folder,
#                                                 '{:02d}'.format(workflow[next_step]['stage']),
#                                                 str(workflow[next_step]['name'])))
            
#         create_folder(path,folder,newfolder)

#         new_path = '/'.join([path,folder,
#                             newfolder])

#         for file in os.listdir(folder_path):

#             if file not in files:
#                 os.rename('/'.join([folder_path,file]), '/'.join([new_path,file]))   


#         metafolder = ''.join(['','metadata'])

#         metapath = create_folder(new_path,'',metafolder)

#         for file in os.listdir(new_path):
#             if file.endswith('ply'):
#                 pass
#             else:
#                 file_split = file.split('.')

#                 if file_split[len(file_split)-2] in workflow[next_step]['metadata']:

#                     os.rename('/'.join([new_path,file]), '/'.join([metapath,file]))
