import os
import joblib
import numpy as np

#Getting the data of training set
def getTrainData(pkl_train):
    if (os.path.exists(pkl_train)):
        m_train = joblib.load(pkl_train)
        m_train = np.array(m_train)
        all_unit1=len(m_train[0])
        m_train0=m_train.copy()
        m_train0=m_train0-2
        zero_array = np.where(m_train0, 0, 1) 
        hybridNumTrain = np.sum(zero_array)  
        del m_train0,zero_array
    return m_train,hybridNumTrain,all_unit1

#Getting the data of testing set for reconstruction imputation
def resGetTestData(dataA_Name,dataA_pkl_path,dataB_Name,loop_i,dirPath):
    dataA_pos=[]
    dataB_pos=[]
    union_pos=[]
    f = open(dirPath+'/postemp/'+str(dataA_Name)+'_templatePos'+str(loop_i+1)+'.txt','r+')
    testAPos1=f.readlines()
    for i in testAPos1:
        rs = i.rstrip('\n')  
        dataA_pos.append(rs)

    if (os.path.exists(dataA_pkl_path)):
        m_testA = joblib.load(dataA_pkl_path)
        all_unit2=len(m_testA)

    f2=open(dirPath+'/postemp/'+str(dataB_Name)+'_templatePos'+str(loop_i+1)+'.txt','r+')
    testBPos1=f2.readlines()
    for i in testBPos1:
        rs = i.rstrip('\n')  
        dataB_pos.append(rs)

    f3=open(dirPath+'/postemp/unionPos'+str(loop_i+1)+'.txt','r+')
    AllPos1=f3.readlines()
    for i in AllPos1:
        rs = i.rstrip('\n')  
        union_pos.append(rs)
    return dataA_pos,dataB_pos,union_pos,m_testA,all_unit2

#Getting the data of testing set for general imputation
def impGetTestData(pkl_testyin):
    if (os.path.exists(pkl_testyin)):
        m_testyin = joblib.load(pkl_testyin)
        m_testyin = np.array(m_testyin)
        m_testyin = m_testyin.T
        all_unit2 = len(m_testyin[0])
    return m_testyin,all_unit2

#Getting the data information message of testing set for reconstructiong imputation
def RESgetTestMSG(dataA_Name,dataA_pkl_path,dataB_Name,dirPath):
    dataA_pos=[]
    dataB_pos=[]
    union_pos=[]
    f = open(dirPath+'/postemp/'+str(dataA_Name)+'_templatePos.txt','r+')
    testAPos1=f.readlines()
    for i in testAPos1:
        rs = i.rstrip('\n')  
        dataA_pos.append(rs)

    if (os.path.exists(dataA_pkl_path)):
        m_testA = joblib.load(dataA_pkl_path)
        all_unit2=len(m_testA)

    f2=open(dirPath+'/postemp/'+str(dataB_Name)+'_templatePos.txt','r+')
    testBPos1=f2.readlines()
    for i in testBPos1:
        rs = i.rstrip('\n')  
        dataB_pos.append(rs)

    f3=open(dirPath+'/postemp/'+str(dataA_Name) + '_' + str(dataB_Name) + '_union.txt','r+')
    AllPos1=f3.readlines()
    for i in AllPos1:
        rs = i.rstrip('\n')  
        union_pos.append(rs)
    loci_num=len(union_pos)
    missingNum=0
    n=0
    for i in range(len(union_pos)):
                if(union_pos[i] in dataB_pos and union_pos[i] not in dataA_pos ):
                    for m in range(len(m_testA)):
                        missingNum=missingNum+1
                else:
                    for m in range(len(m_testA)):
                        if m_testA[m][n] ==0:
                            missingNum=missingNum+1
                    n=n+1
    missing_rate=missingNum/(loci_num*all_unit2)
    missing_rate=round(missing_rate*100,2)
    return loci_num,all_unit2,missing_rate

#Getting the data information message of testing set for general imputation
def IMPgetTestMSG(pkl_testyin):
    if (os.path.exists(pkl_testyin)):
        m_testyin = joblib.load(pkl_testyin)
        m_testyin = np.array(m_testyin)
        m_testyin = m_testyin.T
        all_unit2 = len(m_testyin[0])
        loci_num=len(m_testyin)
        missingNum = np.sum(m_testyin == 0 )
        missing_rate=missingNum/(loci_num*all_unit2)
        missing_rate=round(missing_rate*100,2)
    return loci_num,all_unit2,missing_rate