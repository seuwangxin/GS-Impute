#Installation of the software
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('-i', nargs='?', type=str)

args = parser.parse_args()
i = args.i

install_GS_Cmd = 'python setup.py install'
if i is not None:
    source=str(i)
    install_pyqt5_Cmd ='pip3 install -i '+source+' pyqt5'
    install_pandas_cmd = 'pip3 install -i '+source+' pandas'
    install_scikit_cmd ='pip3 install -i '+source+' scikit-learn'
else:
    install_pyqt5_Cmd ='pip3 install pyqt5'
    install_pandas_cmd = 'pip3 install pandas'
    install_scikit_cmd ='pip3 install scikit-learn'
subprocess.getoutput(install_GS_Cmd)

try:
    scheduler_order = install_pyqt5_Cmd
    return_info = subprocess.Popen(scheduler_order, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        next_line = return_info.stdout.readline()
        return_line = next_line.decode("utf-8", "ignore")
        if return_line == '' and return_info.poll() != None:
            break
    returncode = return_info.wait()
    if returncode:
        raise subprocess.CalledProcessError(returncode, return_info)
except Exception as e:
    print(e)

try:
    scheduler_order = install_pandas_cmd
    return_info = subprocess.Popen(scheduler_order, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        next_line = return_info.stdout.readline()
        return_line = next_line.decode("utf-8", "ignore")
        if return_line == '' and return_info.poll() != None:
            break
    returncode = return_info.wait()
    if returncode:
        raise subprocess.CalledProcessError(returncode, return_info)
except Exception as e:
    print(e)

try:
    scheduler_order =install_scikit_cmd
    return_info = subprocess.Popen(scheduler_order, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        next_line = return_info.stdout.readline()
        return_line = next_line.decode("utf-8", "ignore")
        if return_line == '' and return_info.poll() != None:
            break
    returncode = return_info.wait()
    if returncode:
        raise subprocess.CalledProcessError(returncode, return_info)
except Exception as e:
    print(e)

try:
    import torch 
except Exception as e:
    print('ERROR：'+str(e))
print('GS-Impute successfully installed! You can execute \'gsi\' to run GS-Impute.')