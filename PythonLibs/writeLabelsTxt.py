import numpy as np
import timeit

def write_header(file):
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | txt file with labels                                |\n")
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | Format: index label                                 |\n")
    file.write("# +-----------------------------------------------------+\n")

def write_funval_header(file,funval):
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | txt file with funvals ({})                            ".format(funval)[:-len(funval)] + "|\n")
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | Format: index funval                                |\n")
    file.write("# +-----------------------------------------------------+\n")

def write_funvals_txt_file(label_dict, target_file):
    start_timer = timeit.default_timer()
    
    f = open(target_file + ".txt", "w")
      
    write_header(f)
    
    # write labels
    for index,label in label_dict.items():
        f.write(str(index) + " " + str(label) + "\n")

    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing label txt file:', time_writing_file)


def write_labels_txt_file(label_dict, target_file):
    start_timer = timeit.default_timer()
    
    f = open(target_file + ".txt", "w")
      
    write_header(f)
    
    # write labels
    for index,label in label_dict.items():
        f.write(str(index) + " " + str(label) + "\n")

    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing label txt file:', time_writing_file)

def write_funvals_txt_file(funval_dict, target_file,funval):
    start_timer = timeit.default_timer()
    
    f = open("{}{}.txt".format(target_file,funval), "w")
      
    write_funval_header(f,funval) 

    # write funvals
    for index,funval in funval_dict.items():
        f.write(str(index) + " " + str(funval) + "\n")

    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing funval txt file:', time_writing_file)

def write_funval_thresh_labels_txt_file(vert_dict, thresh, target_file):
    start_timer = timeit.default_timer()
    
    f = open(target_file + str(thresh) + "thresh.txt", "w")
      
    write_header(f)
    
    # write labels
    for ind, vert in vert_dict.items():
        if vert.fun_val < thresh:
            f.write(str(ind) + " " +str(1) + "\n")
        else:
            f.write(str(ind) + " " +str(2) + "\n")
        
    f.close()
    time_writing_file = timeit.default_timer() - start_timer
    print('Time writing label txt file:', time_writing_file)
 
