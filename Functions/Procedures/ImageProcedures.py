import os 
from minions.ImageMinions import import_labelme_annotations

def annotation_image_procedure (obj,**kwargs):

    root = kwargs['root']
    publication = kwargs['publication']
    folder = kwargs['folder']
    processed_folder = kwargs['processed_folder']

    path = ''.join([root,publication])
    files = os.listdir(''.join([path,folder]))

    for file in files:
        filename = file[:-4]
        if file.endswith('.png') and ''.join([filename,'.json']) in files: 

            import_labelme_annotations  (path,filename,folder,processed_folder) 