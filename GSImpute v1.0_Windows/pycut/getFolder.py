import os
import pathlib
#Creating a folder
def mkdir(path):
    reslPath=path
    folder = os.path.exists(reslPath)
    if not folder:
        os.makedirs(reslPath)  

#Removing a folder
def delete_local_dir(delete_path):
    path = pathlib.Path(delete_path)
    for i in path.glob("**/*"):
        if (os.path.exists(i)):
            if (os.path.isfile(i)):
                os.remove(i)
    a = []
    for i in path.glob("**/*"):
        a.append(str(i))
    a.sort(reverse=True)
    for i in a:
        if (os.path.exists(i)):
            if (os.path.isdir(i)):
                os.removedirs(i)
    if (os.path.exists(delete_path)): 
        os.removedirs(delete_path)