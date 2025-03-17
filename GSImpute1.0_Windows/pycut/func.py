import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import manhattan_distances
from scipy.spatial import distance
from sklearn.impute import KNNImputer

#Data coding
def lociConvert(geneData,missing_code):
    missNum=0
    hybridNum=0
    for i in range(len(geneData)):
        for j in range(len(geneData[0])):
            if geneData[i][j] == "0|0" or geneData[i][j] == "0/0":
                geneData[i][j] = 1
            elif geneData[i][j] == "1|1" or geneData[i][j] == "1/1":
                geneData[i][j] = 3
            elif geneData[i][j] == "2|2" or geneData[i][j] == "2/2":
                geneData[i][j] = 3
            elif geneData[i][j] == ".|." or geneData[i][j] == "./.": 
                geneData[i][j] = missing_code
                missNum = missNum+1
            else:
                geneData[i][j] = 2
                hybridNum=hybridNum+1
    return geneData,missNum,hybridNum

#Getting the index of missing test data
def getTestAllMissing_index(testyin_x):
    testAllMissing_index = [[] for i in range(len(testyin_x))]
    for i in range(len(testyin_x)):
        for j in range(len(testyin_x[i])):
            if (testyin_x[i][j] == 0):
                testAllMissing_index[i].append(j)
    return testAllMissing_index

#Getting the index of window data
def getWindowMissing_index(Missing_index,start,trueStart,end,window_size):
    returnMissing_index = [[] for i in range(len(Missing_index))]
    AllMissingLen = 0
    for i in range(len(Missing_index)):
        AllMissingLen = AllMissingLen + len(Missing_index[i])
        for j in range(len(Missing_index[i])):
            if (Missing_index[i][j] >= start and Missing_index[i][j] < end):
                if (trueStart == start): 
                    returnMissing_index[i].append(Missing_index[i][j] % window_size)
                else:  
                    returnMissing_index[i].append((Missing_index[i][j] + start - trueStart) % window_size)
    return returnMissing_index,AllMissingLen

#Determining if it is duplicated
def isRepeat(id, lenOftrain, repeat):
    repeat=np.array(repeat)
    if ((id % lenOftrain) in (repeat % lenOftrain)):
        return True
    else:
        return False

#The function for calculating distance
def cal_dist(train_x,testyin_x):
    train_num = int(len(train_x))
    meanList= np.mean(train_x, axis=0)
    testyin_x2=testyin_x.copy()
    testyin_x2 = np.float_(testyin_x2)  
    for j in range(len(testyin_x2[0])):
        testyin_x2[np.argwhere(testyin_x[:, j] == 0), j] = meanList[j]
    distArray = manhattan_distances(testyin_x2, train_x)
    distMean = np.mean(distArray, axis=1)
    argdistMean = distMean.argsort()[::-1]
    del distMean
    argTrain=[]
    distArray = pd.DataFrame(distArray)
    while len(argTrain) < train_num:
        for i in argdistMean:
            id_min = distArray.iloc[i].drop(argTrain).idxmin()
            argTrain.append(id_min)
            if(len(argTrain)==train_num):
                break
    del distArray
    k=0
    train_x_corrupt=train_x.copy()
    for i in range(train_num):
        for j in range(len(testyin_x[0])):
            if testyin_x[argdistMean[k]][j] == 0:
                train_x_corrupt[argTrain[i],j] = 0
        k = k+1
        if(k==len(testyin_x)):
            k = 0
    del argTrain, argdistMean,testyin_x
    return train_x, train_x_corrupt

#The function for matching test samples
def cal_distImpute2(testyin_x, testyin_x_knn):
    train_num = int(len(testyin_x))
    distArray=manhattan_distances(testyin_x_knn, testyin_x_knn)
    row, col = np.diag_indices_from(distArray)
    distArray[row, col] = np.max(distArray) * 2
    distMean = np.mean(distArray, axis=1)
    argdistMean = distMean.argsort()[::-1]
    argTrain = []
    distArray = pd.DataFrame(distArray)
    train_num_selected = int(np.floor(train_num*1))
    while len(argTrain) < train_num_selected:
        for i in argdistMean:
            id_min = distArray.iloc[i].drop(argTrain).idxmin()  
            argTrain.append(id_min)
            if (len(argTrain) == train_num_selected):
                break
    argdistMean2 = distMean.argsort()
    argTrain2 = []
    while len(argTrain2) < train_num_selected:
        for i in argdistMean2:
            id_min = distArray.iloc[i].drop(argTrain2).idxmin() 
            argTrain2.append(id_min)
            if (len(argTrain2) == train_num_selected):
                break
    del distArray
    argTrain_sort = set(argTrain).union(set(argTrain2))
    argTrain_sort = np.array(list(argTrain_sort))
    argTrain_sort.sort()
    testyin_x2 = testyin_x_knn.copy()
    for i in range(len(argTrain)):
        for j in range(len(testyin_x[0])):
            if (testyin_x[argdistMean[i]][j] == 0) and (testyin_x[argTrain[i]][j] != 0):
                testyin_x2[argTrain[i]][j] = 0
            if (testyin_x[argdistMean2[i]][j] == 0) and (testyin_x[argTrain2[i]][j] != 0):
                testyin_x2[argTrain2[i]][j] = 0
    testyin_x = testyin_x_knn[argTrain_sort, :]
    testyin_x_corrupt = testyin_x2[argTrain_sort, :]
    del testyin_x2
    return testyin_x, testyin_x_corrupt

#The function for matching samples
def cal_distImpute(train_x, testyin_x):
    train_num = int(len(train_x))
    testyin_x0 = testyin_x.copy()
    testyin_x3 = knnImputer(testyin_x0)
    meanList = np.mean(train_x, axis=0)
    testyin_x2 = testyin_x.copy()
    testyin_x2 = np.float_(testyin_x2)
    for j in range(len(testyin_x2[0])):
        testyin_x2[np.argwhere(testyin_x2[:, j] == 0), j] = meanList[j]
    testyin_x0 = testyin_x.copy()
    Matching_results = cal_distImpute2(testyin_x0, testyin_x3)
    distArray=manhattan_distances(testyin_x2, train_x)
    distMean = np.mean(distArray, axis=1)
    argdistMean = distMean.argsort()[::-1]  
    del distMean
    argTrain = []
    distArray = pd.DataFrame(distArray)
    while len(argTrain) < train_num:
        for i in argdistMean:
            id_min = distArray.iloc[i].drop(argTrain).idxmin()  
            argTrain.append(id_min)
            if (len(argTrain) == train_num):
                break
    del distArray
    k = 0
    train_x_corrupt=train_x.copy()
    for i in range(train_num):
        for j in range(len(testyin_x[0])):
            if testyin_x[argdistMean[k]][j] == 0:
                train_x_corrupt[argTrain[i],j]=0
        k = k + 1
        if (k == len(testyin_x)):
            k = 0
    del argTrain, argdistMean
    train_x = np.vstack([train_x, Matching_results[0]])
    train_x_corrupt = np.vstack([train_x_corrupt, Matching_results[1]])
    return train_x, train_x_corrupt

#The function for getting scaled distances
def inverse_distance_weights(distances):
    distances = np.where(distances <= 0, 1e-6, distances)
    scaled_distances = distances / np.max(distances)
    return np.exp(-44 * np.log(scaled_distances))

#The function for knn
def knnImputer(train_x):
    train_x = np.float_(train_x)
    train_x[train_x == 0] = np.nan
    imputer = KNNImputer(n_neighbors=5, weights='distance')  
    train_x_copy = imputer.fit_transform(train_x)
    train_x_copy = np.pad(train_x_copy, ((0, 0), (0, len(train_x[0]) - len(train_x_copy[0]))), mode='mean')
    train_x_copy = np.round(train_x_copy).astype(int)
    return train_x_copy