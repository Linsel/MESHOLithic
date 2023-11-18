import os,sys

currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from Functions.EssentialDecorators import timing
from Functions.exportFiles.writeTxtHeader import write_labels_header,write_links_header,write_links_eval_header,write_funval_header


# LABELS

####
# write labels values    

@timing
def write_labels_txt_file(label_dict, target_file):

    f = open(''.join([target_file, ".txt"]), "w")
      
    write_labels_header(f)
    
    # write labels
    for index,label in label_dict.items():
        f.write(''.join([ str(index),' ',str(label),'\n']))


# LINKS        

####
# write links values          

@timing
def write_links_csv_file(edges: set, target_file:str):

    f = open(''.join([target_file, ".csv"]), "w")
      
    write_links_header(f)
    
    # write labels
    for source,target in edges:
        f.write(''.join([ str(source),',',str(target),'\n']))        

####
# write links eval values      

@timing
def write_links_eval_csv_file(label_dict, target_file):

    f = open(''.join([target_file, ".csv"]), "w")
      
    write_links_eval_header(f)
    
    # write labels
    for index,label in label_dict.items():
        f.write(''.join([ str(' '.join([str(i) for i in index])),',',str(label),'\n']))        


# FUNCTION VALUES      

####
# write function values    
# 

@timing
def write_funvals_txt_file(funval_dict, target_file,funval):
    
    f = open(''.join([target_file, funval]), "w")
      
    write_funval_header(f,funval) 

    # write funvals
    for index,funval in funval_dict.items():
        f.write(''.join([ str(index),' ',str(funval),"\n"]))

####
# write function values  tresholded 
# 
        
@timing
def write_funval_thresh_labels_txt_file(vert_dict, thresh, target_file):
    
    f = open(''.join([ str(target_file),str(thresh),'thresh.txt']), "w")
      
    write_funval_header(f)
    
    # write labels
    for index, vert in vert_dict.items():
        if vert.fun_val < thresh:
            f.write(''.join([ str(index),' ',str(1),"\n"]))
        else:
            f.write(''.join([ str(index),' ',str(2),"\n"]))
        
 
