import math
import pycut.getFolder
import csv
import pycut.getVcf
import pycut.getPkl

class MyException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return f"{self.code}: {self.message}"

#Getting position information
def getPosIndex(vcf_path,vcf_name,out,dirPath,chr=None):
    if vcf_path is not None  :
        if chr is None:
            with open(vcf_path, encoding='utf-8-sig') as f:  
                f_csv = csv.reader(f, delimiter='\t')
                for row in f_csv:
                        if row[0][0] != '#':
                            chr=row[0]
                            break
            pycut.getFolder.mkdir(dirPath+'/postemp')
            posNone=getPosFromVcf(vcf_path,out,dirPath)
        else:
            pycut.getVcf.getVcfByChr(vcf_path,vcf_name,chr,dirPath)
            pycut.getFolder.mkdir(dirPath+'/postemp')
            posNone=getPosFromVcf(dirPath+'/vcfOutput/'+vcf_name+'Chr'+str(chr)+'.vcf',out,dirPath)
    else:
        print("Input data is missing!")
    if posNone==-1:
        return posNone
    else:
        return chr

#Getting position information from a vcf file
def getPosFromVcf(vcf_path,out,dirPath):
    pos_list=[]
    with open(vcf_path, encoding='utf-8-sig') as f:
            row=f.readline()
            while(row):
                if row[0] != '#':
                   break
                row=f.readline()
            while(row):
                t1_index = row.find('\t')
                t2_index = row.find('\t',t1_index+1)
                pos_list.append(row[t1_index+1:t2_index]+'\n')
                row=f.readline()
    try:
        if (len(pos_list)==0):
            raise MyException(100,"POS data none")
    except MyException as e:
        print("Throw an exception：", repr(e))
        return -1
    pos_txt=open(dirPath+'/postemp/' + out + '.txt','w+')
    pos_txt.writelines(pos_list)
    pos_txt.close()
    return 0

#Get position information from a CSV file
def getPosIndexByCsv(csv_path,posIndexTxt,dirPath,chr):
    csvHead=readCsv(csv_path)
    if csvHead==-1:
        return -1
    elif csvHead == -2:
        return -2
    chrIndex=csvHead[0]
    posIndex=csvHead[1]
    fileType=csv_path[-3:]
    if fileType=='csv':
        delimiter=','
    else:
        delimiter='\t'
    pos2=[]
    with open(csv_path, encoding='utf-8-sig') as f:
        for row in csv.reader(f,delimiter=delimiter):
            row1 = row.copy()
            if row1[chrIndex] == chr:
                pos2.append(row1[posIndex]+'\n')
    pycut.getFolder.mkdir(dirPath+'/postemp')
    if len(pos2)==0:
        return -3
    f = open(dirPath+'/postemp/' + posIndexTxt + '.txt', 'w+')
    f.writelines(pos2)
    f.close()
    return chr

#Getting intersection
def getIntersection(data1_pos_txt,data2_pos_txt,posIndex,dirPath):
    if data1_pos_txt is not None and data2_pos_txt is not None:
        if posIndex is None:
            posIndex ='Intersection'
        f = open(data1_pos_txt, 'r+')
        pos1 = f.readlines()
        f = open(data2_pos_txt , 'r+')
        pos2 = f.readlines()
        pos1=set(pos1)
        pos2=set(pos2)
        intersection=pos1.intersection(pos2)
        intersection=list(intersection)
        intersection.sort(key=lambda x: int(x))
        pycut.getFolder.mkdir(dirPath+'/postemp')
        try:
            if (len(intersection)==0):
                raise MyException(101,"intersection is None")
        except MyException as e:
            print("Throw an exception：", repr(e))
            return -1
        f = open(dirPath+'/postemp/'+posIndex+'.txt', 'w+')
        f.writelines(intersection)
        f.close()
        global IntersectionLen
        IntersectionLen=len(intersection)
        global PrePosLen
        PrePosLen=len(pos1)
    else:
        print("Input data is missing!")

#Getting union
def getUnion(data1_pos_txt, data2_pos_txt, posIndex,dirPath):
    if data1_pos_txt is not None and data2_pos_txt is not None:
        if posIndex is None:
            posIndex = 'Union'
        f = open(data1_pos_txt , 'r+')
        pos1 = f.readlines()
        f = open(data2_pos_txt , 'r+')
        pos2 = f.readlines()
        union = list(set(pos1) | (set(pos2)))
        union.sort(key=lambda x: int(x))
        union=list(union)
        pycut.getFolder.mkdir(dirPath+'/postemp')
        f = open(dirPath+'/postemp/'+posIndex + '.txt', 'w+')
        f.writelines(union)
        f.close()
    else:
        print("Input data is missing!")

#Getting the subset of a panel
def getUnionSubset(panel_path,panel_name,union_name,dirPath,window_size,chr):
    eachSubset=12000 
    pos_txt=union_name+ '_union.txt'
    f = open(dirPath + '/postemp/'+pos_txt, 'r+')
    pos = f.readlines()
    f.close()
    if len(pos)<=eachSubset:
        loop_num=1
    else:
        if len(pos)%eachSubset == 0:
            loop_num=int(len(pos)/eachSubset)
        elif len(pos)%eachSubset < window_size:
            loop_num = int(len(pos) / eachSubset)
        else:
            loop_num=int(len(pos)/eachSubset)+1
    SubsetList = [[] for i in range(loop_num)]

    for j in range(loop_num):
        if j == loop_num-1:
            SubsetList[j].append(pos[j * eachSubset: ])
        else:
            SubsetList[j].append(pos[j * eachSubset: (j+1) * eachSubset])

    for i in range(len(SubsetList)):
        f = open(dirPath + '/postemp/unionPos' + str(i+1) + '.txt', 'w+')
        f.writelines(SubsetList[i][0])
        f.close()
    pycut.getPkl.getPklByvcf(union_name+ '_union.vcf', 0,dirPath,'')
        
    for i in range(len(SubsetList)):
        pycut.getVcf.getVcfByPos(panel_path,panel_name, 
                                 dirPath + '/postemp/unionPos' + str(i+1) + '.txt',
                                 dirPath + '/postemp/' +panel_name + 'pos.txt' ,
                                 'unionSubset'+str(i+1),dirPath,chr,'train')
        pycut.getPkl.getPklByvcf('unionSubset'+str(i+1)+'.vcf', 0,dirPath,i+1)
    del pos,SubsetList
    return loop_num

#Getting the subset of intersection
def getIntersectionSubset(dataName, loop_num, dirPath):
    for l in range(loop_num):
        f = open(dirPath + '/postemp/' + dataName + '_templatePos.txt', 'r+')
        pos = f.readlines()
        f = open(dirPath + '/postemp/' + 'unionPos' + str(l + 1) + '.txt', 'r+')
        union = f.readlines()
        pos=set(pos)
        union=set(union)
        subset=pos.intersection(union)
        subset=list(subset)
        subset.sort(key=lambda x: int(x))
        f = open(dirPath + '/postemp/' + dataName + '_templatePos' + str(l + 1) + '.txt', 'w+')
        f.writelines(subset)
        f.close

#Getting the number of loops
def getLoopNum(txt,dirPath,window_size):
    f = open(dirPath + '/postemp/' + txt, 'r+')
    pos = f.readlines()
    loop_num_all=math.ceil(len(pos) / window_size)
    return loop_num_all

#Geting the subset of training data
def getTrainSubset(panel_path,train_name,dataName,dirPath,window_size,chr):
    eachSubset=12000
    pos_txt=dataName+ '_templatePos.txt'
    f = open(dirPath + '/postemp/'+pos_txt, 'r+')
    pos = f.readlines()
    f.close()
    if len(pos)<=eachSubset:
        loop_num=1
    else:
        if len(pos)%eachSubset == 0:
            loop_num=int(len(pos)/eachSubset)
        elif len(pos)%eachSubset < window_size:
            loop_num = int(len(pos) / eachSubset)
        else:
            loop_num=int(len(pos)/eachSubset)+1
    SubsetList = [[] for i in range(loop_num)]

    for j in range(loop_num):
        if  j == loop_num-1:
            SubsetList[j].append(pos[j * eachSubset: ])
        else:
            SubsetList[j].append(pos[j * eachSubset: (j+1) * eachSubset])

    for i in range(len(SubsetList)):
        f = open(dirPath + '/postemp/TrainPos' + str(i+1) + '.txt', 'w+')
        f.writelines(SubsetList[i][0])
        f.close()
    pycut.getPkl.getPklByvcf(dataName + '_train.vcf', 0,dirPath,'')
    for i in range(len(SubsetList)):
        pycut.getVcf.getVcfByPos(panel_path,
                                 train_name, 
                                 dirPath + '/postemp/TrainPos' + str(i+1) + '.txt', 
                                 dirPath + '/postemp/' +train_name + 'pos.txt' ,
                                 'trainSubset'+str(i+1),dirPath,chr,'train')
        pycut.getPkl.getPklByvcf('trainSubset'+str(i+1)+'.vcf', 0,dirPath,i+1)
    del SubsetList,pos
    return loop_num

#Getting the subset of intersection
def getIntersectionSubset2(dataName, loop_num, dirPath):
    for l in range(loop_num):
        f = open(dirPath + '/postemp/' + dataName + '_templatePos.txt', 'r+')
        pos = f.readlines()
        f = open(dirPath + '/postemp/' + 'TrainPos' + str(l + 1) + '.txt', 'r+')
        train = f.readlines()
        pos=set(pos)
        train=set(train)
        subset=pos.intersection(train)
        subset=list(subset)
        subset.sort(key=lambda x: int(x))
        f = open(dirPath + '/postemp/' + dataName + '_templatePos' + str(l + 1) + '.txt', 'w+')
        f.writelines(subset)
        f.close()

#Getting the subset of a vcf file
def getVcfSubset(data_path,dataName,loop_num,dirPath,chr):
    pycut.getVcf.getVcfByPos(data_path,
                                 dataName, 
                                 dirPath + '/postemp/'+ dataName + '_templatePos.txt', 
                                 dirPath + '/postemp/' +dataName + 'pos.txt',
                                 dataName+'_subset',dirPath,chr)
    pycut.getPkl.getPklByvcf(dataName+'_subset.vcf', 1,dirPath)
    for l in range(loop_num):
        pycut.getVcf.getVcfByPos(data_path,
                                 dataName, 
                                 dirPath + '/postemp/'+ dataName + '_templatePos' + str(l + 1) + '.txt', 
                                 dirPath + '/postemp/' +dataName + 'pos.txt',
                                 dataName+'_subset'+str(l+1),dirPath,chr)
        pycut.getPkl.getPklByvcf(dataName+'_subset'+str(l+1)+'.vcf', 1,dirPath)

#Getting the information of a csv file
def readCsv(csv_path):
    fileType = csv_path[-3:]
    if fileType == 'csv':
        delimiter = ','
    else:
        delimiter = '\t'
    csvHead = []
    with open(csv_path, encoding='utf-8-sig') as f:
        for row in csv.reader(f, delimiter=delimiter):
            row1 = row.copy()
            csvHead.append(row1[0:11])
            break
    for i in range(len(csvHead[0])):
        csvHead[0][i] = str(csvHead[0][i]).lower()[0:3]
    chrCount = csvHead[0].count('chr')
    hashChrCount = csvHead[0].count('#ch')
    posCount = csvHead[0].count('pos')
    refCount = csvHead[0].count('ref')
    altCount = csvHead[0].count('alt')
    QCcodeIndex = csvHead[0].count('qcc')
    indexList = []
    if chrCount == 1:
        chrIndex = csvHead[0].index('chr')
        indexList.append(chrIndex)
    elif hashChrCount == 1:
        chrIndex = csvHead[0].index('#ch')
        indexList.append(chrIndex)
    else:
        print('chr is not found!')
        return -1
    if posCount == 1:
        posIndex = csvHead[0].index('pos')
        indexList.append(posIndex)
    else:
        print('pos is not found!')
        return -2
    if refCount == 1:
        refIndex = csvHead[0].index('ref')
        indexList.append(refIndex)
    if altCount == 1:
        altIndex = csvHead[0].index('alt')
        indexList.append(altIndex)
    if QCcodeIndex == 1:
        QCcodeIndex = csvHead[0].index('qcc')
        indexList.append(QCcodeIndex)
    dataIndex = max(indexList) + 1
    return chrIndex, posIndex, dataIndex