import os, sys


def command_line_GigaMesh(path,name, method, parameters = ' '):
    giga_path = "~/Downloads/build-GigaMesh-Desktop_Qt_5_15_2_GCC_64bit-Debug/cli/"

    print("{0}{1}{2}{3}{4}{5}{6}".format(str(giga_path),str(method),' ', str(parameters), ' ' , str(name) ,'.ply'))

    os.chdir(path)
    
    os.system("{0}{1}{2}{3}{4}{5}{6}".format(str(giga_path),str(method),' ', str(parameters), ' ' , str(name) ,'.ply'))