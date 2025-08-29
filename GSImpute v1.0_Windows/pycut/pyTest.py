import os
import subprocess
#Start of the software
def main():
        upup_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        start_path=upup_path+'/UI/start.py'
        cmd = 'python '+start_path
        subprocess.getoutput(cmd)