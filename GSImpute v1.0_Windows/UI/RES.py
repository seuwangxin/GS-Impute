#Reconstruction imputation interface
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
#Reconstruction imputation interface
def to_RES(self,task_num,data_A_path,data_B_path,panel_path,dirPath):
    window_size=1000
    lock.acquire(1)
    self.pro_Signal.emit(0,0,0,'',task_num)
    task_num=task_num+1
    print(task_num)
    self.task_state_Signal.emit(task_num,'Preprocessing')
    self.task_list_Signal.emit('Task '+str(task_num)+': Start')
    
    SavePath_and_SaveName=dirPath.split('\\')
    SaveName=SavePath_and_SaveName[-1]
    dirPath='\\'.join(SavePath_and_SaveName[0:-1])
    if (data_A_path is not None):
            data_A_path=str(data_A_path)
            data_A_path1=data_A_path.split('\\')
            data1=data_A_path1[-1]
            data1Name = data1[0:-4]
            print(data1Name)

    if (data_B_path is not None):
            data_B_path=str(data_B_path)
            data_B_path1=data_B_path.split('\\')
            data2=data_B_path1[-1]
            data2Name = data2[0:-4]
   
    if (panel_path is not None):
        panel_path=str(panel_path)
        panel_path1=panel_path.split('\\')
        tem=panel_path1[-1]
        temName = tem[0:-4]
    dirPath = dirPath+'/'+'gsi_temp'
    pycut.getFolder.mkdir(dirPath)
    data1Type = data1[-3:]
    data2Type = data2[-3:]

    print("Getting position index")
    self.task_list_Signal.emit('Task '+str(task_num)+': Getting the positions of markers')
    chr=pycut.getPos.getPosIndex(panel_path,temName, temName + 'pos', dirPath)
    if chr == -1:
        self.task_state_Signal.emit(task_num,'Task Error')
        self.task_list_Signal.emit('Error: In '+'task '+str(task_num)+' , no position records of the reference panel are detected!')
        self.task_list_Signal.emit('Task '+str(task_num)+': Task terminated!')
        self.task_error_Signal.emit('Error: In '+'task '+str(task_num)+' , no position records of the reference panel are detected!')
        lock.release()
        return 100
    
    if (data1Type == 'vcf'):
        posNone=pycut.getPos.getPosIndex(data_A_path,data1Name, str(data1Name) + 'pos', dirPath,chr)
        if posNone==-1:
            self.task_state_Signal.emit(task_num,'Task Error')
            self.task_list_Signal.emit('Error: In '+'task '+str(task_num)+' , no position records of the genotype file are detected!')
            self.task_list_Signal.emit('Task '+str(task_num)+': Task terminated!')
            self.task_error_Signal.emit('Error: In '+'task '+str(task_num)+' , no position records of the genotype file are detected!')
            lock.release()
            return 100
        
    elif (data1Type == 'csv' or data1Type == 'txt'):
        posNone=pycut.getPos.getPosIndexByCsv(data_A_path, str(data1Name) + 'pos', dirPath,chr)
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
        print("data1 no input!")

    if (data2Type == 'vcf'):
        posNone=pycut.getPos.getPosIndex(data_B_path,data2Name, str(data2Name) + 'pos', dirPath,chr)
        if posNone==-1:
            self.task_state_Signal.emit(task_num,'Task Error')
            self.task_list_Signal.emit('Error: In '+'task '+str(task_num)+' , no position records of the genotype file are detected!')
            self.task_list_Signal.emit('Task '+str(task_num)+': Task terminated!')
            self.task_error_Signal.emit('Error: In '+'task '+str(task_num)+' , no position records of the genotype file are detected!')
            lock.release()            
            return 100
        
    elif (data2Type == 'csv' or data2Type =='txt'):
        posNone=pycut.getPos.getPosIndexByCsv(data_B_path, str(data2Name) + 'pos', dirPath,chr)
        if posNone==-3:
            self.task_state_Signal.emit(task_num,'Task Error')
            self.task_list_Signal.emit('Error: In '+'task '+str(task_num)+' , no position records of the position file are detected!')
            self.task_list_Signal.emit('Task '+str(task_num)+': Task terminated!')
            self.task_error_Signal.emit('Error: In '+'task '+str(task_num)+' , no position records of the position file are detected!')
            lock.release()
            return 100
        elif posNone == -1:
            self.task_state_Signal.emit(task_num,'Task Error')
            self.task_list_Signal.emit('Error: In '+'task '+str(task_num)+' ,the column chr of the position file is not found!')
            self.task_list_Signal.emit('Task '+str(task_num)+': Task terminated!')
            self.task_error_Signal.emit('Error: In '+'task '+str(task_num)+' ,the column chr of the position file is not found!')
            lock.release()
            return 101
        elif posNone == -2:
            self.task_state_Signal.emit(task_num,'Task Error')
            self.task_list_Signal.emit('Error: In '+'task '+str(task_num)+' ,the column pos of the position file is not found!')
            self.task_list_Signal.emit('Task '+str(task_num)+': Task terminated!')
            self.task_error_Signal.emit('Error: In '+'task '+str(task_num)+' ,the column pos of the position file is not found!')
            lock.release()
            return 102

    print("Getting the intersection of positions")
    self.task_list_Signal.emit('Task '+str(task_num)+': Getting the intersection of positions')
    pycut.getPos.getIntersection(dirPath + '/postemp/' + data1Name + 'pos.txt',
                                    dirPath + '/postemp/' + temName + 'pos.txt', data1Name + '_templatePos', dirPath)
    if pycut.getPos.IntersectionLen<=0:
        self.task_state_Signal.emit(task_num,'Task Error')
        self.task_list_Signal.emit('Error: In '+'task '+str(task_num)+' ,the number of marker intersection between the target genotype file and the reference panel is zero!')
        self.task_list_Signal.emit('Task '+str(task_num)+': Task terminated!')
        lock.release()
        return 200
    prePosLen=pycut.getPos.PrePosLen 
    minLen=prePosLen/10 
   
    if pycut.getPos.IntersectionLen<window_size and pycut.getPos.IntersectionLen>0:
        min_window_size=pycut.getPos.IntersectionLen
        if min_window_size%8==0:
            window_size=min_window_size
        else:
            window_size=(int(min_window_size/8))*8
    if pycut.getPos.IntersectionLen>0 and pycut.getPos.IntersectionLen<=minLen:
        global task_P
        task_P=0
        self.task_warning_Signal.emit('Task '+str(task_num)+' Warning: The number of marker intersection between the target genotype file and the reference panel is only '+str(pycut.getPos.IntersectionLen)+' ! Do you want to continue with the task ?')
        while task_P==0:
            time.sleep(0.5)
        if task_P==-1:
            self.task_state_Signal.emit(task_num,'Task Error')
            self.task_list_Signal.emit('Task '+str(task_num)+': Task terminated!')
            lock.release()
            return
    
    pycut.getPos.getIntersection(dirPath + '/postemp/' + data2Name + 'pos.txt',
                                    dirPath + '/postemp/' + temName + 'pos.txt', data2Name + '_templatePos', dirPath)
    if pycut.getPos.IntersectionLen<=0:
        self.task_state_Signal.emit(task_num,'Task Error')
        self.task_list_Signal.emit('Error: In '+'task '+str(task_num)+' ,the number of marker intersection between the position file and the reference panel is zero!')
        self.task_list_Signal.emit('Task '+str(task_num)+': Task terminated!')
        lock.release()
        return 200
    prePosLen=pycut.getPos.PrePosLen
    minLen=prePosLen/10

    if pycut.getPos.IntersectionLen>0 and pycut.getPos.IntersectionLen<=minLen:
        task_P=0
        self.task_warning_Signal.emit('Task '+str(task_num)+' Warning: The number of marker intersection between the position file and the reference panel is only '+str(pycut.getPos.IntersectionLen)+' ! Do you want to continue with the task ?')
        while task_P==0:
            time.sleep(0.5)
        if task_P==-1:
            self.task_state_Signal.emit(task_num,'Task Error')
            self.task_list_Signal.emit('Task '+str(task_num)+': Task terminated!')
            lock.release()
            return
        
    print("Getting the union of positions")
    self.task_list_Signal.emit('Task '+str(task_num)+': Getting the union of positions')
    pycut.getPos.getUnion(dirPath + '/postemp/' + data1Name + '_templatePos.txt',
                            dirPath + '/postemp/' + data2Name + '_templatePos.txt',
                            data1Name + '_' + data2Name + '_union', dirPath)
    self.task_list_Signal.emit('Task '+str(task_num)+': Getting the panel file for training')
    pycut.getVcf.getVcfByPos(panel_path,
                                temName,
                                dirPath + '/postemp/' + data1Name + '_' + data2Name + '_union.txt',
                                dirPath + '/postemp/' +temName + 'pos.txt',
                                data1Name + '_' + data2Name + '_union', dirPath,chr,'train')
    
    self.task_list_Signal.emit('Task '+str(task_num)+': Segmenting the reference panel')
    subset_num = pycut.getPos.getUnionSubset(panel_path,temName, data1Name + '_' + data2Name, dirPath,window_size,chr)
    train_loop_num=pycut.getPos.getLoopNum(data1Name + '_' + data2Name + '_union.txt', dirPath,window_size)

    self.task_list_Signal.emit('Task '+str(task_num)+': Segmenting the genotype files')
    pycut.getPos.getIntersectionSubset(data1Name, subset_num, dirPath)
    pycut.getPos.getIntersectionSubset(data2Name, subset_num, dirPath)
    if (data1Type == 'vcf'):
        pycut.getVcf.getVcfByPos(data_A_path,data1Name, 
                                    dirPath + '/postemp/' + data1Name + '_templatePos.txt',
                                    dirPath + '/postemp/' +data1Name + 'pos.txt',
                                    data1Name + '_subset', dirPath,chr)
    print('Getting the target data array')
    self.task_list_Signal.emit('Task '+str(task_num)+': Reading the genotype data')
    pycut.getPkl.getResRefAndAlt(data1Name,data2Name,subset_num,dirPath)
    if (data1Type == 'vcf'):
        pycut.getPos.getVcfSubset(data_A_path,data1Name,subset_num,dirPath,chr)
    elif (data1Type == 'csv' or data1Type =='txt'):
        csvData=pycut.getPkl.getPklByCsvFenduan(data_A_path,data1Name, dirPath, subset_num,chr)
        if(csvData==-1):
            self.task_state_Signal.emit(task_num,'Task Error')
            self.task_list_Signal.emit('Error: In '+'task '+str(task_num)+' , format of the target genotype file is unexpected!')
            self.task_list_Signal.emit('Task '+str(task_num)+': Task terminated!')
            self.task_error_Signal.emit('Error: In '+'task '+str(task_num)+' , format of the target genotype file is unexpected!')
            lock.release()
            return 301
    gc.collect() 
    k=pycut.reconstructTask.Restructure(self.task_state_Signal,self.pro_Signal,self.task_list_Signal,data1Name,data1Type, data2Name, dirPath, subset_num,train_loop_num,window_size,task_num)
    if k==-2:
        self.task_state_Signal.emit(task_num,'Completed')
        self.task_error_Signal.emit('In '+'task '+str(task_num)+' , missing markers are not permitted on the panel.')
        self.task_list_Signal.emit('Task '+str(task_num)+': Terminated')
        lock.release()
        return 401
    self.pro_Signal.emit(100,1,1,'Task '+str(task_num)+': Saving the imputation results (may take several minutes)',task_num)
    
    pycut.impute.Impute(data1Name, 'RES', dirPath,subset_num)
    self.task_list_Signal.emit('Task '+str(task_num)+': Saving imputation results')
    pycut.reconstructTask.RESgetCsv(data_A_path,data1Name,data1Type, data2Name, dirPath,SaveName,subset_num)
    pycut.getFolder.delete_local_dir(dirPath)
    self.task_state_Signal.emit(task_num,'Completed')
    self.task_list_Signal.emit('Task '+str(task_num)+': Completed')
    self.pro_Signal.emit(0,0,0,'',0)
    lock.release()
    gc.collect()