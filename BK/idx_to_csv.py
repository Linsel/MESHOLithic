import csv 
import sys

def idx_to_csv (path,file_name):
 
    with open("".join([path,file_name]), newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t', quotechar='"')
        for n,row in enumerate(spamreader):

            if ['', 'POINTS (PointNo, PointID, East, North, Elevation, Code, Date, CLASS)'] == row:
                beg_end = [n]
                temp = row[1][8:-1] 
                export = temp.split(', ')

            if 	['', '', 'THEMINFO (PointNo, PointID, Attribute, Value)'] == row:
                beg_end.append(n)

    with open("".join([path,file_name]), newline='') as csvfile:
        spamreader_2 = csv.reader(csvfile, delimiter='\t', quotechar='"')
        with open('Targets_cleaned.csv', 'w') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_NONE)
            writer.writerow(export)

            for n,row in enumerate(spamreader_2):
                if n in range(beg_end[0],beg_end[1]):
                    
                    if len(row[2:]) == 9 and row[2:][1].startswith('TARGET'):

                        row[3] = ' '.join(['target',row[3][7:]])
                        print(row[3])
                        temp = [ros[:-1] for ros in row[2:-2]] + [row[-1][:-1]]
                        writer.writerow(temp)


if __name__ == "__main__":

    idx_to_csv (sys.argv[1],sys.argv[2])

