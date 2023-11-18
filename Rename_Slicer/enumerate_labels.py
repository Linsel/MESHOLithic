def read_label_txt(filename):
    labels = {}
    with open(filename+".txt", "r") as f:
        for line in f:
            if line[0] == "#":
                continue
            else:
                ind = int(line.split()[0])
                label = int(line.split()[1])
                
                if label not in labels.keys():
                    labels[label] = set()
                    labels[label].add(ind)
                else:
                    labels[label].add(ind)
    return labels

def write_header(file):
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | txt file with labels                                |\n")
    file.write("# +-----------------------------------------------------+\n")
    file.write("# | Format: index label                                 |\n")
    file.write("# +-----------------------------------------------------+\n")
    
def write_enumerated_labels_txt_file(label_dict, target_file):
    f = open(target_file + "_enum.txt", "w")
      
    write_header(f)
    
    # write labels
    for label, indices in enumerate(label_dict.values()):
        # start with label 1 instead of 0
        for index in indices:
            f.write(str(index) + " " + str(label+1) + "\n")
    f.close()
    
def write_sorted_labels_txt_file(label_dict, target_file):
    f = open(target_file + ".txt", "w")#"_sorted.txt", "w")
      
    write_header(f)
    count = 0 
    for label, indices in enumerate(sorted(label_dict.values(), key=lambda kv: len(kv), reverse=True)):

        for index in indices:
            f.write(str(index) + " " + str(label+1) + "\n")
    f.close()
    
def write_sorted_labels_txt_file_switch(label_dict, target_file, switch1, switch2):
    f = open(target_file + ".txt", "w")#"_sorted.txt", "w")
      
    write_header(f)
    
    for label, indices in enumerate(sorted(label_dict.values(), key=lambda kv: len(kv), reverse=True)):
        # start with label 1 instead of 0
        if label+1 == switch1:
            for index in indices:
                f.write(str(index) + " " + str(switch2+7) + "\n")
        elif label+1 == switch2:
            for index in indices:
                f.write(str(index) + " " + str(switch1+7) + "\n")
        else:
            for index in indices:
                f.write(str(index) + " " + str(label+8) + "\n")
    f.close()