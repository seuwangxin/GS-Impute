#General imputation interface
import threading
import time
import pycut.getVcf
import pycut.getPos
import pycut.getFolder
import pycut.getPkl
import pycut.reconstructTask
import pycut.impute
import pycut.imputeTask
import gc

lock = threading.Lock()
#General imputation interface
def to_IMP(self,task_num,data_A_path,panel_path,dirPath): 
    window_size=1000
    lock.acquire(1)
    self.pro_Signal.emit(0,0,0,'',0)
    task_num=task_num+1
    self.task_state_Signal.emit(task_num,'Preprocessing')
    self.task_list_Signal.emit('Task '+str(task_num)+': Start')
    SavePath_and_SaveName=dirPath.split('\\')
    SaveName=SavePath_and_SaveName[-1]
    dirPath='\\'.join(SavePath_and_SaveName[0:-1])
    
    if (data_A_path is not None):
            data_A_path=str(data_A_path)
            data_A_path1=data_A_path.split('\\')
            data=data_A_path1[-1]
            dataName = data[0:-4]
            print(dataName)
    else:
        print("No input data!")

    if (panel_path is not None):
        panel_path=str(panel_path)
        panel_path1=panel_path.split('\\')
        tem=panel_path1[-1]
        temName = tem[0:-4]
    else:
        print("No panel!")
    dirPath = dirPath+'/'+'gsi_temp'
    pycut.getFolder.mkdir(dirPath)
    dataType = data[-3:]
    print("Getting position index")
    self.task_list_Signal.emit('Task '+str(task_num)+': Getting the positions of markers')
    chr=pycut.getPos.getPosIndex(panel_path,temName, temName + 'pos', dirPath)
    if chr == -1:
        self.task_state_Signal.emit(task_num,'Task Error')
        self.task_list_Signal.emit('Error: In '+'task '+str(task_num)+' , no position records of reference panel are detected!')
        self.task_list_Signal.emit('Task '+str(task_num)+': Task terminated!')
        self.task_error_Signal.emit('Error: In '+'task '+str(task_num)+' , no position records of reference panel are detected!')
        lock.release()
        return 100
    if (dataType == 'vcf'):
        posNone=pycut.getPos.getPosIndex(data_A_path,dataName, str(dataName) + 'pos', dirPath,chr)
        if posNone==-1:
            self.task_state_Signal.emit(task_num,'Task Error')
            self.task_list_Signal.emit('Error: In '+'task '+str(task_num)+' , no position records of the genotype file are detected!')
            self.task_list_Signal.emit('Task '+str(task_num)+': Task terminated!')
            self.task_error_Signal.emit('Error: In '+'task '+str(task_num)+' , no position records of the genotype file are detected!')
            lock.release()
            return 100
    elif (dataType == 'csv' or dataType == 'txt'):
        posNone=pycut.getPos.getPosIndexByCsv(data_A_path, str(dataName) + 'pos', dirPath,chr)
        if posNone==-3:
            self.task_state_Signal.emit(task_num,'Task Error')
            self.task_list_Signal.emit('Error: In '+'task '+str(task_num)+' , no position records of the genotype file are detected!')
            self.task_list_Signal.emit('Task '+str(task_num)+': Task terminated!')
            self.task_error_Signal.emit('Error: In '+'task '+str(task_num)+' , no position records of the genotype file are detected!')
            lock.release()
            return 100
        elif posNone == -1:
            self.task_state_Signal.emit(task_num,'Task Error')
            self.task_list_Signal.emit('Error: In '+'task '+str(task_num)+' ,the column chr of the genotype file is not found!')
            self.task_list_Signal.emit('Task '+str(task_num)+': Task terminated!')
            self.task_error_Signal.emit('Error: In '+'task '+str(task_num)+' ,the column chr of the genotype file is not found!')
            lock.release()
            return 101
        elif posNone == -2:
            self.task_state_Signal.emit(task_num,'Task Error')
            self.task_list_Signal.emit('Error: In '+'task '+str(task_num)+' ,the column pos of the genotype file is not found!')
            self.task_list_Signal.emit('Task '+str(task_num)+': Task terminated!')
            self.task_error_Signal.emit('Error: In '+'task '+str(task_num)+' ,the column pos of the genotype file is not found!')
            lock.release()
            return 102            
        
    else:
        print("No input data!")
    print("Chrom:"+str(chr))
    print("Getting intersection index")
    self.task_list_Signal.emit('Task '+str(task_num)+': Getting the intersection of positions')
    pycut.getPos.getIntersection(dirPath + '/postemp/' + dataName + 'pos.txt',
                                    dirPath + '/postemp/' + temName + 'pos.txt', dataName + '_templatePos', dirPath)
    if pycut.getPos.IntersectionLen<=0:
        self.task_state_Signal.emit(task_num,'Task Error')
        self.task_list_Signal.emit('Error: In '+'task '+str(task_num)+' ,the number of marker intersection between the unimputed genotype file and the reference panel is zero!')
        self.task_list_Signal.emit('Task '+str(task_num)+': Task terminated!')
        lock.release() 
        return 200
    prePosLen=pycut.getPos.PrePosLen
    minLen=int(prePosLen/10)

    if pycut.getPos.IntersectionLen<window_size and pycut.getPos.IntersectionLen>0:
        print('bug 0')
        min_window_size=pycut.getPos.IntersectionLen
        print(min_window_size)
        print(min_window_size%8)
        print((int(min_window_size/8))*8)
        if min_window_size%8==0:
            window_size=min_window_size
        else:
            window_size=(int(min_window_size/8))*8
        window_size=int(window_size)
        print(window_size)
    if pycut.getPos.IntersectionLen>0 and pycut.getPos.IntersectionLen<=minLen:
        global task_P
        task_P=0
        self.task_warning_Signal.emit('Task '+str(task_num)+' Warning: The number of marker intersection between the unimputed genotype file and the reference panel is only '+str(pycut.getPos.IntersectionLen)+' ! Do you want to continue with the task ?')
        while task_P==0:
            time.sleep(0.5)

        if task_P==-1:
            self.task_state_Signal.emit(task_num,'Task Error')
            self.task_list_Signal.emit('Task '+str(task_num)+': Task terminated!')
            lock.release()
            return
    print("Getting the panel file for training")
    self.task_list_Signal.emit('Task '+str(task_num)+': Getting the panel file for training')
    pycut.getVcf.getVcfByPos(panel_path,temName, 
                                dirPath + '/postemp/' + dataName + '_templatePos.txt', 
                                dirPath + '/postemp/' +temName + 'pos.txt',
                                dataName + '_train', 
                                dirPath,chr,'train')
    print("Getting the panel subset")
    self.task_list_Signal.emit('Task '+str(task_num)+': Segmenting the panel')
    
    subset_num = pycut.getPos.getTrainSubset(panel_path,temName, dataName, dirPath,window_size,chr)
    train_loop_num=pycut.getPos.getLoopNum(dataName + '_templatePos.txt', dirPath,window_size)
    print("train_loop_num:"+str(train_loop_num))
    print('Getting ' + str(subset_num) + ' segments')
    print('Getting intersection subset')
    self.task_list_Signal.emit('Task '+str(task_num)+': Segmenting the genotype files')
    pycut.getPos.getIntersectionSubset2(dataName, subset_num, dirPath)

    if (dataType == 'vcf'):
        pycut.getVcf.getVcfByPos(data_A_path,dataName, 
                                    dirPath + '/postemp/' + dataName + '_templatePos.txt' , 
                                    dirPath + '/postemp/' +dataName + 'pos.txt',
                                    dataName + '_subset', dirPath,chr)
    print('Getting genotype data in PKL format')
    self.task_list_Signal.emit('Task '+str(task_num)+': Reading the genotype data')
    pycut.getPkl.getPklByvcf(dataName + '_train.vcf', 0,dirPath)
    if (dataType == 'vcf'):
        print('Getting the testing subset')
        pycut.getPos.getVcfSubset(data_A_path,dataName,subset_num,dirPath,chr)
    elif (dataType == 'csv' or dataType == 'txt'):
        print('Getting PKL data with a CSV file')
        csvData=pycut.getPkl.getPklByCsvFenduan(data_A_path,dataName, dirPath, subset_num,chr)
        if(csvData==-1):
            self.task_state_Signal.emit(task_num,'Task Error')
            self.task_list_Signal.emit('Error: In '+'task '+str(task_num)+' , genotype format of the target file is unexpected!')
            self.task_list_Signal.emit('Task '+str(task_num)+': Task terminated!')
            self.task_error_Signal.emit('Error: In '+'task '+str(task_num)+' , genotype format of the target file is unexpected!')
            lock.release()
            return 301
    else:
        print("NO input data!")
  
    k=pycut.imputeTask.ImputeTask(self.task_state_Signal,self.pro_Signal,self.task_list_Signal,dataName,dataType,subset_num,train_loop_num,window_size,dirPath,task_num)
    if k==-1:
        self.task_state_Signal.emit(task_num,'Completed')
        self.task_error_Signal.emit('In '+'task '+str(task_num)+' , there are no missing markers detected, and imputation is unnecessary.')
        self.task_list_Signal.emit('Task '+str(task_num)+': Terminated')
        lock.release()
        return 401
    if k==-2:
        self.task_state_Signal.emit(task_num,'Completed')
        self.task_error_Signal.emit('In '+'task '+str(task_num)+' , missing markers are not permitted on the panel.')
        self.task_list_Signal.emit('Task '+str(task_num)+': Terminated')
        lock.release()
        return 401
    self.pro_Signal.emit(100,1,1,'Task '+str(task_num)+': Saving imputation results (may take several minutes)',task_num)
    self.task_list_Signal.emit('Task '+str(task_num)+': Saving imputation results')
    
    if dataType == 'csv' or dataType == 'txt' :
        pycut.reconstructTask.IMPgetTxtOrCsv(data_A_path,dataName,dataType, dirPath,SaveName,chr,subset_num)
    else:
        pycut.reconstructTask.IMPgetVcf(dataName,dirPath,SaveName,subset_num)
    pycut.getFolder.delete_local_dir(dirPath)
    self.task_state_Signal.emit(task_num,'Completed')
    self.task_list_Signal.emit('Task '+str(task_num)+': Completed')
    self.pro_Signal.emit(0,0,0,'',0)
    gc.collect()
    lock.release()