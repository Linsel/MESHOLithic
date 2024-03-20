import os,sys

currentdir = os.getcwd()
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from Functions.EssentialDecorators import timing

# LABELS

def write_labels_header(file):
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | txt file with labels                                |\n")
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | Format: index label                                 |\n")
    file.write("# +-----------------------------------------------------+\n")

# LINKS

def write_links_header(file):
    file.write("source,target\n")    

def write_links_eval_header(file):
    file.write("links,eval\n")  

# FUNCTION VALUES

def write_funval_header(file,funval):
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | txt file with funvals ({})                            ".format(funval)[:-len(funval)] + "|\n")
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | Format: index funval                                |\n")
    file.write("# +-----------------------------------------------------+\n")

# FEATURE VECTORS

def write_feature_vectors_header(file,fv):
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | txt file with funvals ({})                            ".format(fv)[:-len(fv)] + "|\n")
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | Format: index funval                                |\n")
    file.write("# +-----------------------------------------------------+\n")