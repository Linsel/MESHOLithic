from DataMinions import *

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