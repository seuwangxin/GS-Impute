import torch
import joblib
import logging, os
logging.disable(logging.WARNING)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import warnings
warnings.filterwarnings("ignore")
import math
import os
import random as rn
import numpy as np
from pycut.func import getTestAllMissing_index
from pycut.func import cal_distImpute
from pycut.input import getTrainData,impGetTestData,IMPgetTestMSG
from pycut.getPos import getLoopNum
from pycut.model import train_func
import gc
from pycut.getPos import MyException

gc.set_threshold(700, 10, 5)

#Executing the task of general imputation
def ImputeTask(task_state_Signal,pro_signal,task_list_Signal,dataName,dataType,time,loop_num_all,window_size,dirPath,task_num):
    stride=1
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    seed_value = 1234
    os.environ['TF_DETERMINISTIC_OPS'] = '1'
    os.environ['PYTHONHASHSEED'] = str(seed_value)
    rn.seed(seed_value)
    np.random.seed(seed_value)
    epochs = 150
    filter_size = 15
    batch_size = 64  
    learning_rate = 1e-3

    global nowEpochNum
    nowEpochNum=0
    global epochNumTemp
    epochNumTemp=0
    global Allepochs
    Allepochs=0

    if dataType == 'vcf':
        testA_all_pkl_path = dirPath+'/pkl/'+str(dataName)+'_subset.vcfPkl.pkl'
    elif dataType =='csv' or dataType =='txt' :
        testA_all_pkl_path = dirPath+'/pkl/' + str(dataName) + 'Pkl.pkl'
    else:
        print("The genotype file is none!")
    all_imp_test_data=IMPgetTestMSG(testA_all_pkl_path)
    task_list_Signal.emit('Task '+str(task_num)+': The number of samples for imputation is '+str(all_imp_test_data[1]))
    task_list_Signal.emit('Task '+str(task_num)+': The number of loci for imputation is '+str(all_imp_test_data[0]))
    task_list_Signal.emit('Task '+str(task_num)+': The missing rate of markers is '+ str(all_imp_test_data[2])+'%')
    task_list_Signal.emit('Task '+str(task_num)+': Training in progress')
    task_state_Signal.emit(task_num,'Imputing')

    for loop_i in range(time):
        pkl_train = dirPath+'/pkl/'+'trainSubset'+str(loop_i+1)+'.vcfPkl.pkl'
        train_data=getTrainData(pkl_train)
        m_train=train_data[0]
        try:
            if (np.any(m_train == 0)):
                raise MyException(101,"Missing markers are not permitted on the panel")
        except MyException as e:
            print("Throw an exception：", repr(e))
            return -2
        num = len(m_train)
        m_train = np.array(m_train)
        os.environ['PYTHONHASHSEED'] = str(seed_value)
        rn.seed(seed_value)
        np.random.seed(seed_value)
        predict_missing_all5 = []
        missingNum = 0
        if dataType == 'vcf':
            pkl_testyin = dirPath+'/pkl/'+str(dataName)+'_subset'+str(loop_i+1)+'.vcfPkl.pkl'
        elif dataType =='csv' or dataType =='txt':
            pkl_testyin = dirPath+'/pkl/' + str(dataName) +str(loop_i+1)+ 'Pkl.pkl'
        else:
            print("The genotype file is none!")
        test_data=impGetTestData(pkl_testyin)
        m_testyin=test_data[0]
        all_unit2=test_data[1]

        for i in range(len(m_testyin)):
            for j in range(len(m_testyin[i])):
                if m_testyin[i][j]== 0:
                    missingNum=missingNum+1
        if missingNum==0:
            return -1
        
        m_testyin = np.array(m_testyin)
        testyin_x = m_testyin.T
        testyin_x_pkl_path =dirPath+'/pkl/testyin_x'+str(loop_i+1)+'.pkl'
        joblib.dump(testyin_x,testyin_x_pkl_path)
        del m_testyin
        
        TestAllMissing_index = getTestAllMissing_index(testyin_x)
        trainyin_x = m_train.copy()
        trainyin_x = trainyin_x.T

        Matching_results = cal_distImpute(trainyin_x, testyin_x)  
        trainyin_x = Matching_results[0] - 1
        train_corrupt=Matching_results[1]
        del Matching_results

        missing_rate = missingNum / (num * all_unit2)
        drop_perc=0.3-((missing_rate-0.1)/8)
        missing_rate=round(missing_rate*100,2)
        if window_size>=1000 and missing_rate>95 and num>=1400:
            window_size=1400
        loop_num_all=getLoopNum(dataName + '_templatePos.txt', dirPath,window_size)
        loop_num = math.ceil(num / window_size)
        Allepochs=loop_num*epochs
        epoch_num_all = epochs*loop_num_all
        end = 0  
        predictAll = [[] for i in range(all_unit2)]
        predictAll=train_func(pro_signal,task_num,loop_num,epochs,epoch_num_all,epochNumTemp,window_size,num,TestAllMissing_index,trainyin_x,testyin_x,train_corrupt,batch_size,drop_perc,filter_size,stride,device,learning_rate,all_unit2,predictAll,end)
        del trainyin_x, testyin_x
        
        predict_missing_all5.append(predictAll)
        del predictAll
        str_miss_path = dirPath+'/'+'pkl/'+str(dataName)+'_IMPpredict'+str(loop_i+1)+'.pkl'
        joblib.dump(predict_missing_all5, str_miss_path)
        del predict_missing_all5
        epochNumTemp=epochNumTemp+Allepochs
    del device
    torch.cuda.empty_cache()
    gc.collect()    
    return 0