import os,sys,json
from minions.FolderMinions import *

# currentdir = os.getcwd()
# parentdir = os.path.dirname(currentdir)
# sys.path.insert(0, currentdir) 
# sys.path.insert(0, parentdir) 

from Functions.main import procedures

def export_workflow (path, 
                     folder, 
                     workflow,
                     steps):    
    
    workflow_path = "/".join([path,
                              folder,
                              ''.join(['workflow-',
                                       '-'.join(steps),
                                       '.json'])
                              ])

    # workflow export 

    with open(workflow_path,"w") as f:
        json.dump(workflow,f)

def run_workflow (path, 
                  folder, 
                  workflow):

    last_step = get_last_step (path,folder,workflow)
    
    steps = [v['name'] for v in workflow.values()]
    max_steps = max([v['stage'] for v in workflow.values()])

    export_workflow(path, folder, workflow, steps)

    for n in range(last_step[0],max_steps):

        workflow_step (path,folder,workflow,n)


def workflow_step (path,folder,workflow,n):

    next_step = n + 1

    newfolder = '_'.join([  folder,
                            str("{:02d}".format(workflow[n]['stage'])),
                            workflow[n]['name']])

    folder_path = '/'.join([path,
                            folder,
                            newfolder,
                            ''])

    files = os.listdir(folder_path)


    if workflow[next_step]['add_labels'] == True:

        kwargs = {
            'path':path, 
            'folder':folder,
            'newfolder':newfolder,
            'filename':workflow[next_step]['labelname']}
        
        # add_labels(**kwargs)
        label_paths = get_file_paths(**kwargs)
        

    if workflow[next_step]['add_links'] == True:

        kwargs = {
            'path':path, 
            'folder':folder,
            'newfolder':newfolder,
            'filename':workflow[next_step]['linkname']}  
                        
        # add_links(**kwargs)
        link_paths = get_file_paths(**kwargs)
                

    for file in files:
        # try:
        print ("Begin to process {}".format(file))
        if file.endswith('ply'):

            temp_kwargs = { 'path':folder_path,
                            'id':file[:-4],
                            'class':workflow[next_step]['class'],
                            'method':workflow[next_step]['method'],
                            'parameters': workflow[next_step]['parameters']}
            
            temp_kwargs.update(workflow[next_step]['variables'])

            if workflow[next_step]['add_labels'] == True:

                print(label_paths)

                temp_kwargs['labelfilepath'] = label_paths[file.split('_')[0]]
                

            if workflow[next_step]['add_links'] == True:

                print(link_paths)

                temp_kwargs['linkfilepath'] = link_paths [file.split('_')[0]] 
       

            procedures (**temp_kwargs)

        # except: 
            # print ("Something went wrong while calculating {}".format(file))
            # continue
                
    if workflow[next_step]['method'] != '':

        newfolder = str("{}_{}_{}".format(  folder,
                                                '{:02d}'.format(workflow[next_step]['stage']),
                                                str(workflow[next_step]['name'])))
            
        create_folder(path,folder,newfolder)

        new_path = '/'.join([path,folder,
                            newfolder])

        for file in os.listdir(folder_path):

            if file not in files:
                os.rename('/'.join([folder_path,file]), '/'.join([new_path,file]))   


        metafolder = ''.join(['','metadata'])

        metapath = create_folder(new_path,'',metafolder)

        for file in os.listdir(new_path):
            if file.endswith('ply'):
                pass
            else:
                file_split = file.split('.')

                if file_split[len(file_split)-2] in workflow[next_step]['metadata']:

                    os.rename('/'.join([new_path,file]), '/'.join([metapath,file]))
