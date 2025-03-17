import csv
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
import pandas as pd 
from pycut.model import Autoencoder,MyDataSet, train_func
from pycut.getPos import getLoopNum,readCsv
from pycut.getPkl import hmp_line_encoding
from pycut.func import getTestAllMissing_index,getWindowMissing_index
from pycut.func import cal_dist
from pycut.input import RESgetTestMSG,getTrainData,resGetTestData
import torch
from torch import nn
import torch.nn.functional as F
import torch.optim as optim
import gc

def Restructure(data1Name,data1Type,data2Name,dirPath,time,loop_num_all,window_size):
    stride=1
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    seed_value = 1234
    os.environ['TF_DETERMINISTIC_OPS'] = '1'
    os.environ['PYTHONHASHSEED'] = str(seed_value)
    rn.seed(seed_value)
    np.random.seed(seed_value)
    epochs = 150
    filter_size = 15
    batch_size =64
    learning_rate = 1e-3
   
    global nowEpochNum
    nowEpochNum=0
    global epochNumTemp
    epochNumTemp=0
    global Allepochs
    Allepochs=0

    if data1Type == 'vcf':
        testA_all_pkl_path = dirPath+'/pkl/'+str(data1Name)+'_subset.vcfPkl.pkl'
    elif data1Type =='csv' or data1Type =='txt':
        testA_all_pkl_path = dirPath+'/pkl/' + str(data1Name)+ 'Pkl.pkl'
    else:
        print("The genotype file is none!")

    all_res_test_data=RESgetTestMSG(data1Name,testA_all_pkl_path,data2Name,dirPath)
    print("The number of loci for imputation is "+str(all_res_test_data[0]))
    print("The number of samples for imputation is "+str(all_res_test_data[1]))
    print("The missing rate of markers is " + str(all_res_test_data[2]))
    print('Training in progress')

    for loop_i in range(time):
        pkl_train = dirPath+'/pkl/'+'unionSubset'+str(loop_i+1)+'.vcfPkl.pkl'
        train_data = getTrainData(pkl_train)
        m_train,hybridNumTrain,all_unit1 = train_data[0],train_data[1],train_data[2]
        num=len(m_train)
        m_train = np.array(m_train)
        os.environ['PYTHONHASHSEED'] = str(seed_value)
        rn.seed(seed_value)
        np.random.seed(seed_value)
        missingNum=0
        
        if data1Type == 'vcf':
            testA_pkl_path = dirPath+'/pkl/'+str(data1Name)+'_subset'+str(loop_i+1)+'.vcfPkl.pkl'
        elif data1Type =='csv' or data1Type=='txt':
            testA_pkl_path = dirPath+'/pkl/' + str(data1Name) +str(loop_i+1)+ 'Pkl.pkl'
        else:
            print("The genotype file is none!")

        res_Test_Data=resGetTestData(data1Name,testA_pkl_path,data2Name,loop_i,dirPath)
        dataA_pos=res_Test_Data[0]
        dataB_pos=res_Test_Data[1]
        union_pos=res_Test_Data[2]
        m_testA=res_Test_Data[3]
        all_unit2=res_Test_Data[4]
        m_testyin = []
        list_testyin=[]
        n=0
        for i in range(len(union_pos)):
            if(union_pos[i] in dataB_pos and union_pos[i] not in dataA_pos ):
                for m in range(len(m_testA)):
                    list_testyin.append(0)
                    missingNum=missingNum+1
            else:
                for m in range(len(m_testA)):
                    list_testyin.append(m_testA[m][n])
                    if m_testA[m][n] ==0:
                        missingNum=missingNum+1
                n+=1
        for i in range(0, len(list_testyin), int(all_unit2)):
            list0 = list_testyin[i:i + int(all_unit2)]
            m_testyin.append(list0)
        m_testyin = np.array(m_testyin)
        testyin_x = m_testyin.T
        testyin_x_pkl_path =dirPath+'/pkl/testyin_x'+str(loop_i+1)+'.pkl'
        joblib.dump(testyin_x,testyin_x_pkl_path)
        del m_testyin
        
        TestAllMissing_index = getTestAllMissing_index(testyin_x)
        trainyin_x = m_train.copy()
        trainyin_x =trainyin_x.T
        
        Matching_results = cal_dist(trainyin_x,testyin_x)
        trainyin_x = Matching_results[0] - 1
        train_corrupt=Matching_results[1]
        del Matching_results

        missing_rate=missingNum/(num*all_unit2)
        drop_perc=0.3-((missing_rate-0.1)/8)

        missing_rate=round(missing_rate*100,2)
        
        if window_size>=1000 and missing_rate>95 and num>=1400:
            window_size=1400
        loop_num_all=getLoopNum(data1Name + '_' + data2Name + '_union.txt', dirPath,window_size)
        loop_num = math.ceil(num / window_size)
        Allepochs=loop_num*epochs
        epoch_num_all = epochs*loop_num_all
        end = 0 
        predictAll=[[] for i in range(all_unit2)]
        predictAll=train_func(loop_num,epochs,epoch_num_all,epochNumTemp,window_size,num,TestAllMissing_index,trainyin_x,testyin_x,train_corrupt,batch_size,drop_perc,filter_size,stride,device,learning_rate,all_unit2,predictAll,end)
        del trainyin_x, testyin_x
        predict_missing_all5 = []
        predict_missing_all5.append(predictAll)
        del predictAll
        str_miss_path = dirPath+'/pkl/'+str(data1Name)+'_RESpredict'+str(loop_i+1)+'.pkl'
        joblib.dump(predict_missing_all5, str_miss_path)
        del predict_missing_all5
        epochNumTemp=epochNumTemp+Allepochs
        gc.collect()

def RESgetCsv(data_A_path,data1Name,data1Type, data2Name,dirPath,saveName,loop_num,save_path):
    sampleName = []
    chrom = []
    vcfId = []
    REFList = []
    ALTList = []
    POSList = []
    str_train = dirPath+'/vcfOutput/' + str(data1Name) + '_' + str(data2Name) + '_union.vcf'
    valid_data = False
    with open(str_train, encoding='utf-8-sig') as f:  
        f_csv = csv.reader(f, delimiter='\t')
        for row in f_csv:
            if valid_data:
                chrom.append(row[0])
                POSList.append(row[1])
                idStr = str(str(row[0]) + '_' + str(row[1]))
                vcfId.append(idStr)
                REFList.append(row[3])
                ALTList.append(row[4])
            else:
                if row[0][0] != '#':
                    chrom.append(row[0])
                    POSList.append(row[1])
                    idStr = str(str(row[0]) + '_' + str(row[1]))
                    vcfId.append(idStr)
                    REFList.append(row[3])
                    ALTList.append(row[4])
                    valid_data = True
    
    if data1Type == 'vcf':
        str_test = dirPath+'/vcfOutput/' + str(data1Name) + '_subset.vcf'
        with open(str_test, encoding='utf-8-sig') as f:  
            f_csv = csv.reader(f, delimiter='\t')
            for row in f_csv:
                    if row[0][1] != '#':
                        sampleName.append(row[9:])
                        break
        sampleName=sampleName[0]
    elif data1Type == 'csv' or data1Type == 'txt':
        dataIndex=readCsv(data_A_path)[2]
        csvData = []
        fileType=data_A_path[-3:]
        if fileType=='csv':
            delimiter=','
        else:
            delimiter='\t'
        with open(data_A_path, encoding='utf-8-sig') as f:
            for row in csv.reader(f,delimiter=delimiter):
                row1 = row.copy()
                csvData.append(row1)
        for i in range(len(csvData[0]) - dataIndex):
            sampleName.append(csvData[0][i + dataIndex])
    else:
        print("Data type error")

    start=0
    for loop in range(loop_num):
        str_result = dirPath+'/pkl/' + str(data1Name) + '_RESfinalOutput'+str(loop+1)+'.pkl'
        resultData = joblib.load(str_result)  
        end=start+len(resultData[0])

        DataSet = zip(vcfId[start:end], chrom[start:end], POSList[start:end], REFList[start:end],ALTList[start:end])
        df = pd.DataFrame(data=DataSet, columns=['ID', 'CHROM', 'POS', 'REF','ALT'])
        start=end

        dic = dict()
        for i in range(len(sampleName)):
            name = str(sampleName[i])
            dic[name] = resultData[i]
        new_df = pd.DataFrame(dic)
        df = pd.concat([df, new_df], axis=1)

        str_csv = save_path
        if loop==0:
            df.to_csv(str_csv, index=False)
        else:
            df.to_csv(str_csv,mode='a',index=False,header=False)
    
def IMPgetTxtOrCsv(data_A_path,data1Name,data1Type,dirPath,saveName,chr,loop_num,save_path):
    headLine=[]
    isHead=1
    csvHead=readCsv(data_A_path)
    chrIndex=csvHead[0]
    posIndex=csvHead[1]
    dataIndex=csvHead[2]

    if data1Type == 'csv' or data1Type == 'txt':
        fileType=data_A_path[-3:]
        if fileType=='csv':
            delimiter=','
        else:
            delimiter='\t'

    for loop in range(loop_num):
        f = open(dirPath+'/postemp/'+str(data1Name)+'_templatePos'+str(loop+1)+'.txt','r+')
        testAPos=f.read().splitlines()
        all_data_row=[]
        with open(data_A_path, encoding='utf-8-sig') as f:
                for row in csv.reader(f,delimiter=delimiter):
                    if isHead!=1:
                        if row[chrIndex] == chr and row[posIndex] in testAPos :
                            all_data_row.append(row)
                    else:
                            headLine.append(row)
                            isHead=-1
        all_data_row.sort(key=lambda x:int(x[posIndex]))
        all_data_row=np.array(all_data_row)
        vcfRowList=all_data_row[:,0:dataIndex]
        GTline=all_data_row[:,dataIndex:]
        del all_data_row
        str_result = dirPath+'/pkl/'+str(data1Name)+'_'+'IMPpredict'+str(loop+1)+'.pkl'
        resultData = joblib.load(str_result)
        resultData = resultData[0]
        GTline=np.array(GTline)
        GTline=GTline.T
        for i in range(len(GTline)):
                k=0
                for j in range(len(GTline[i])):
                    if GTline[i][j]== 'NN' or GTline[i][j]== 'NA' :
                        GTline[i][j]=resultData[i][k]
                        k=k+1

        pkl_ref = dirPath + '/pkl/REF'+str(loop+1)+'.pkl'
        ref = joblib.load(pkl_ref)
        pkl_alt = dirPath + '/pkl/ALT'+str(loop+1)+'.pkl'
        alt = joblib.load(pkl_alt)
        GTline=GTline.T
        new_result_data=[]
        for i in range(len(ref)):
            new_result_line=hmp_line_encoding(GTline[i],ref[i],alt[i])
            new_result_data.append(new_result_line)
        vcfRowList=np.array(vcfRowList)
        new_result_data=np.array(new_result_data)
        vcfRowList=vcfRowList.T
        new_result_data=new_result_data.T
        vcfRowList=vcfRowList.tolist()
        new_result_data=new_result_data.tolist()
        vcfRowList.extend(new_result_data)
        vcfRowList=np.array(vcfRowList)
        vcfRowList=vcfRowList.T
        headLine.extend(vcfRowList)
        print('save_path:'+str(save_path))
        str_txt = save_path
       
        if loop==0:
            vcfWriter = open(str_txt,'w',newline='')
            for line in headLine:
                allLine=delimiter.join(line)
                allLine=allLine+'\n'
                vcfWriter.write(allLine)
            vcfWriter.close()
        else:
            vcfWriter = open(str_txt,'a',newline='')
            for line in vcfRowList:
                allLine=delimiter.join(line)
                allLine=allLine+'\n'
                vcfWriter.write(allLine)
            vcfWriter.close()
        
def IMPgetVcf(dataName,dirPath,saveName,loop_num,save_path):
    for loop in range(loop_num):
        vcf_path = dirPath+'/vcfOutput/' + str(dataName) +  '_subset'+str(loop+1)+'.vcf'
        vcfRowList=[]
        headLine=[]
        with open(vcf_path, encoding='utf-8-sig') as f:
                for row in csv.reader(f,delimiter='\t'):
                    if row[0][0]!='#':
                        vcfRowList.append(row)
                    else:
                            headLine.append(row)
        slash='/'
        slash00='0'+slash+'0'
        slash11='1'+slash+'1'
        slash01='0'+slash+'1'
        slashNan='.'+slash+'.'
        pkl = dirPath+'/pkl/'+str(dataName)+'_'+'IMPpredict'+str(loop+1)+'.pkl'
        pklData = joblib.load(pkl)
        pklData = pklData[0]
        
        for i in range(len(pklData)):
            for j in range(len(pklData[i])):
                if pklData[i][j]== 1:
                    pklData[i][j]=slash00
                elif pklData[i][j]== 3:
                    pklData[i][j]=slash11
                elif pklData[i][j]== 2:
                    pklData[i][j]=slash01
                else:
                    pklData[i][j]=slashNan
        
        vcfRowList=np.array(vcfRowList)
        vcfRowList=vcfRowList.T
        for i in range(len(vcfRowList)-9):
                k=0
                for j in range(len(vcfRowList[i+9])):
                    if vcfRowList[i+9][j][0:3]== '.|.' or vcfRowList[i+9][j][0:3]== './.':
                        vcfRowList[i+9][j]=vcfRowList[i+9][j].replace(vcfRowList[i+9][j][0:3],pklData[i][k],1)
                        k=k+1
        vcfRowList=vcfRowList.T
        vcfRowList=vcfRowList.tolist()
        headLine.extend(vcfRowList)
        print('save_path:'+str(save_path))
        str_vcf = save_path
        if loop==0:
            vcfWriter = open(str_vcf,'w',newline='')
            for line in headLine:
                allLine='\t'.join(line)
                allLine=allLine+'\n'
                vcfWriter.write(allLine)
            vcfWriter.close()
        else:
            vcfWriter = open(str_vcf,'a',newline='')
            for line in vcfRowList:
                allLine='\t'.join(line)
                allLine=allLine+'\n'
                vcfWriter.write(allLine)
            vcfWriter.close()