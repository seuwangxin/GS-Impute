import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('-i', nargs='?', type=str)
args = parser.parse_args()
i = args.i

install_GS_Cmd = 'python setup.py install'
if i is not None:
    source=str(i)
    install_pandas_cmd = 'pip3 install -i '+source+' pandas'
    install_scikit_cmd ='pip3 install -i '+source+' scikit-learn'
else:
    install_pandas_cmd = 'pip3 install pandas'
    install_scikit_cmd ='pip3 install scikit-learn'
subprocess.getoutput(install_GS_Cmd)

print("\n=== Installing pandas ===")
try:
    return_info = subprocess.Popen(install_pandas_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        next_line = return_info.stdout.readline()
        if not next_line and return_info.poll() is not None:
            break
        line = next_line.decode("utf-8", "ignore").strip()
        if line:
            print(line)
    if return_info.returncode:
        raise subprocess.CalledProcessError(return_info.returncode, install_pandas_cmd)
except Exception as e:
    print(f"=== pandas installation failed! Error: {str(e)} ===")

print("\n=== Installing scikit-learn ===")
try:
    return_info = subprocess.Popen(install_scikit_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        next_line = return_info.stdout.readline()
        if not next_line and return_info.poll() is not None:
            break
        line = next_line.decode("utf-8", "ignore").strip()
        if line:
            print(line)
    if return_info.returncode:
        raise subprocess.CalledProcessError(return_info.returncode, install_scikit_cmd)
except Exception as e:
    print(f"=== scikit-learn installation failed! Error: {str(e)} ===")

print("\n=== Checking PyTorch installation ===")
try:
    import torch
    print(f"PyTorch is installed (version: {torch.__version__})")
    print('GS-Impute installed successfully! Type gsi to start.')
except Exception as e:
    print('GS-Impute installed successfully!')
    print(f"Warning: Please install pytorch and then type gsi to run GS-Impute.")