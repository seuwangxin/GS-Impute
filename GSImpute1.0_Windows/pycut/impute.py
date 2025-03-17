import joblib
import os
import random as rn
import numpy as np

#Inserting prediction results into the original file
def Impute(vcfData,type,dirPath,loop_num):
    for i in range(loop_num):
        pkl = dirPath+'/pkl/'+str(vcfData)+'_'+str(type)+'predict'+str(i+1)+'.pkl'
        pklData = joblib.load(pkl)
        testyin_x = []
        pkl_testyin = dirPath+'/pkl/testyin_x'+str(i+1)+'.pkl'
        if (os.path.exists(pkl_testyin)):
            testyin_x = joblib.load(pkl_testyin)
        else:
            print("The pkl file is missing!")
        afterImpute=impute_data(pklData,testyin_x)
        pkl_path = dirPath+'/pkl/'+ str(vcfData) + '_' +str(type)+'finalOutput'+str(i+1)+'.pkl'
        joblib.dump(afterImpute, pkl_path)

#Inserting prediction results into an array
def impute_data(pklData,testyin_x):
        pklDataArr=pklData.copy()
        testyinArr=testyin_x.copy()
        for i in range(len(testyinArr)):
            k=0
            for j in range(len(testyinArr[0])):
                if testyinArr[i][j]== 0:
                    testyinArr[i][j]=pklDataArr[0][i][k]
                    k=k+1
        return testyinArr