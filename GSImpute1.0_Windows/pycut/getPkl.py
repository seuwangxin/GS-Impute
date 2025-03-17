import joblib
import numpy as np
import pycut.getFolder
import pycut.getPos
import csv

#Getting PKL data with a vcf file
def getPklByvcf(vcfdata,type,dirPath,getRefAndAlt=-1):
    m_train=[]
    str_train = dirPath+'/vcfOutput/'+str(vcfdata)
    allREF=[]
    allALT=[]
    valid_data = False
    with open(str_train, encoding='utf-8-sig') as f:  
        f_csv = csv.reader(f, delimiter='\t')
        for row in f_csv:
            
            if valid_data:
                gt=[]
                if getRefAndAlt!=-1:
                    allREF.append(row[3])
                    allALT.append(row[4])
                for geno in row[9:]:
                    gt.append(geno[0:3])
                m_train.append(gt)
            else:
                if row[0][0] != '#':
                    gt = []
                    if getRefAndAlt!=-1:
                        allREF.append(row[3])
                        allALT.append(row[4])
                    for geno in row[9:]:
                        gt.append(geno[0:3])
                    m_train.append(gt)
                    valid_data = True
    m_train = np.array(m_train)
    f.close()
    pycut.getFolder.mkdir(dirPath+'/pkl')
    if getRefAndAlt!=-1:
        pkl_ref = dirPath + '/pkl/REF'+str(getRefAndAlt)+'.pkl'
        joblib.dump(allREF, pkl_ref)
        pkl_alt = dirPath + '/pkl/ALT'+str(getRefAndAlt)+'.pkl'
        joblib.dump(allALT, pkl_alt)
    m_train=np.array(m_train)
    m_train=array_encoding(m_train)
    pkl_train=dirPath+'/pkl/'+vcfdata+'Pkl.pkl'
    pkl_train
    if(type==1):
        m_train=m_train.T
    joblib.dump(m_train, pkl_train)
    del m_train,allALT,allREF,gt
    
#Getting SNP data from a CSV file
def getSnpFromCSV(csvData1,refdata,altdata,dataIndex):
    csvData = csvData1.copy()
    snp_len = len(csvData[0][dataIndex + 0])
    csvData=np.array(csvData)
    csvDataLine=csvData[:,dataIndex:]
    if snp_len== 2:
        for i in range(len(csvDataLine)):
            ref = refdata[i]
            alt = altdata[i]
            csvDataLine[i]=csv_array_encoding(csvDataLine[i],ref,alt)
        csvDataLine=csvDataLine.astype('int32')
        csvDataLine=csvDataLine.tolist()
    elif snp_len == 3: 
        csvDataLine=array_encoding(csvDataLine)
        csvDataLine=csvDataLine.astype('int32')
        csvDataLine=csvDataLine.tolist()
    else:
        print("Data Error !")
        return -1
    return csvDataLine

#Getting PKL from a CSV segement
def getPklByCsvFenduan(csv_path,csvFile,dirPath,loop_num,chr):
    csvData = []
    csvHead=pycut.getPos.readCsv(csv_path)
    chrIndex=csvHead[0]
    posIndex=csvHead[1]
    dataIndex=csvHead[2]
    fileType=csv_path[-3:]
    if fileType=='csv':
        delimiter=','
    else:
        delimiter='\t'
    with open(csv_path, encoding='utf-8-sig') as f:
        for row in csv.reader(f,delimiter=delimiter):
            row1 = row.copy()
            if row1[chrIndex] == chr:
                csvData.append(row1)
    f.close()
    for k in range(loop_num+1):
        if k==0:
            k=''
        f = open(dirPath+'/postemp/' +csvFile + '_templatePos'+str(k)+'.txt', 'r+')
        delList = f.readlines()
        f.close()
        delList2 = []
        for i in delList:
            rs = i.rstrip('\n')  
            delList2.append(rs)
        del delList

        csvData2 = []
        for i in range(len(csvData)):
            temp=str(csvData[i][posIndex])
            if temp in delList2:
                csvData2.append(csvData[i])
        csvData2.sort(key=lambda x:int(x[posIndex]))
        pkl_ref = dirPath + '/pkl/REF' + str(k) + '.pkl'
        pkl_alt = dirPath + '/pkl/ALT' + str(k) + '.pkl'
        ref = joblib.load(pkl_ref)
        alt = joblib.load(pkl_alt)
        snpDataList = getSnpFromCSV(csvData2,ref,alt,dataIndex)
        del csvData2
        if snpDataList== -1:
            return -1
        snpDataList = np.array(snpDataList)
        snpDataList = snpDataList.T
        pycut.getFolder.mkdir(dirPath+'/pkl')
        pkl_testyin = dirPath+'/pkl/'+csvFile+str(k)+'Pkl.pkl'
        joblib.dump(snpDataList, pkl_testyin)
        del snpDataList
    del csvData

#Merging PKL seggments
def mergePkl(loop_num, data1Name, dirPath,type):
    pkl_path = dirPath + '/pkl/' + str(data1Name) + '_'+type+'predict' + str(1) + '.pkl'
    testyinPkl_path = dirPath + '/pkl/testyin_x' + str(1) + '.pkl'
    pklData1 = joblib.load(pkl_path)
    testyinPkl1 = joblib.load(testyinPkl_path)
    testyinPkl1 = testyinPkl1.tolist()
    all_unit = len(pklData1[0])
    if loop_num - 1 > 0:
        for k in range(loop_num - 1):
            pkl_path = dirPath + '/pkl/' + str(data1Name) + '_'+type+'predict' + str(k + 2) + '.pkl'
            pklData = joblib.load(pkl_path)
            testyinPkl_path = dirPath + '/pkl/testyin_x' + str(k + 2) + '.pkl'
            testyinPkl = joblib.load(testyinPkl_path)
            testyinPkl = testyinPkl.tolist()
            for i in range(all_unit):
                pklData1[0][i].extend(pklData[0][i])
                testyinPkl1[i].extend(testyinPkl[i])
    mergePkl1 = dirPath + '/pkl/' + data1Name + '_'+type+'predict.pkl'
    mergePkl2 = dirPath + '/pkl/testyin_x.pkl'
    joblib.dump(pklData1, mergePkl1)
    joblib.dump(testyinPkl1, mergePkl2)

#Encoding vcf data
def array_encoding(array):
    array_copy=array.copy()
    array_copy[np.where( (array_copy=='0/1') | (array_copy=='1/0') | (array_copy=='0|1') | (array_copy=='1|0') | (array_copy=='0/2') | (array_copy=='2/0') | (array_copy=='0|2') | (array_copy=='2|0') | (array_copy=='1/2') | (array_copy=='2/1') | (array_copy=='1|2') | (array_copy=='2|1'))]=2
    array_copy[np.where((array_copy=='1/1') | (array_copy=='1|1') | (array_copy=='2/2') | (array_copy=='2|2'))]=3
    array_copy[np.where((array_copy=='0/0') | (array_copy=='0|0'))]=1
    array_copy[np.where((array_copy!='1') & (array_copy!='2') & (array_copy!='3'))]=0
    array_copy=array_copy.astype('int32')
    return array_copy

#Encoding csv data
def csv_array_encoding(array,ref,alt):
    array_copy=array.copy()
    al2=''
    commaIndex=alt.find(',')
    if len(ref)>=2:
        re=str(ref[0])
        al=str(ref[1])
    else:
        re=ref
        if len(alt)==1:
            al=alt[0]
        else:
            if commaIndex == -1:
                al=str(alt[1])
            else:
                al=alt[commaIndex-1]
                al2=alt[commaIndex+1]
    if al2=='':
        array_copy[np.where(array_copy==(re+re))]=1
        array_copy[np.where((array_copy==(re+al)) | (array_copy==(al+re)))]=2
        array_copy[np.where(array_copy==(al+al))]=3       	
        array_copy[np.where((array_copy=='NA')|(array_copy=='NN'))]=0
        array_copy[np.where((array_copy!='0')&(array_copy!='1')&(array_copy!='2')&(array_copy!='3'))]=2
        array_copy=array_copy.astype('int32')
    else:
        array_copy[np.where((array_copy==(re+re)))]=1
        array_copy[np.where((array_copy==(re+al)) | (array_copy==(al+re))|(array_copy==(re+al2)) | (array_copy==(al2+re)))]=2
        array_copy[np.where((array_copy==(al+al))|(array_copy==(al2+al2)))]=3
        array_copy[np.where((array_copy==(re+re)))]=1
        array_copy[np.where( (array_copy=='NA')|(array_copy=='NN'))]=0
        array_copy[np.where( (array_copy!='0')&(array_copy!='1')&(array_copy!='2')&(array_copy!='3'))]=2
        array_copy=array_copy.astype('int32')
    return array_copy

#Encoding hmp data
def hmp_line_encoding(GTrow,refs,alts):
    GTrow=np.array(GTrow)
    GTrow_copy=GTrow.copy()
    GTrow_copy=GTrow_copy.astype(str)
    if len(refs)==1:
        ref=refs[0]
        alt = alts[0]
    else:
        ref=refs[0]
        alt=refs[1]
    GTrow_copy[np.where((GTrow_copy=='1'))]=ref+ref
    GTrow_copy[np.where((GTrow_copy=='2'))]=ref+alt
    GTrow_copy[np.where((GTrow_copy=='3'))]=alt+alt
    return GTrow_copy

#getting ref and alt for a reconstruction task
def getResRefAndAlt(data1Name,data2Name,loop_num,dirPath):
    pkl_ref = dirPath + '/pkl/REF.pkl'
    allREF=joblib.load(pkl_ref)
    pkl_alt = dirPath + '/pkl/ALT.pkl'
    allALT=joblib.load( pkl_alt)
    data1_pos_str=dirPath + '/postemp/' + data1Name + '_templatePos.txt'
    f = open(data1_pos_str , 'r+')
    data1_pos = f.readlines()
    f.close()
    union_pos_str=dirPath + '/postemp/' + data1Name + '_' + data2Name + '_union.txt'
    f = open(union_pos_str , 'r+')
    union_pos = f.readlines()
    f.close()
    ref=[]
    alt=[]
    for i in range(len(union_pos)):
        if union_pos[i] in data1_pos:
            ref.append(allREF[i])
            alt.append(allALT[i])
    joblib.dump(ref,pkl_ref)
    joblib.dump(alt,pkl_alt)
    for loop in range(loop_num):
        pkl_ref = dirPath + '/pkl/REF'+str(loop+1)+'.pkl'
        allREF=joblib.load(pkl_ref)
        pkl_alt = dirPath + '/pkl/ALT'+str(loop+1)+'.pkl'
        allALT=joblib.load( pkl_alt)
        data1_pos_str=dirPath + '/postemp/' + data1Name + '_templatePos'+str(loop+1)+'.txt'
        f = open(data1_pos_str , 'r+')
        data1_pos = f.readlines()
        f.close()
        union_pos_str=dirPath + '/postemp/unionPos'+str(loop+1)+'.txt'
        f = open(union_pos_str , 'r+')
        union_pos = f.readlines()
        f.close()
        ref=[]
        alt=[]
        for i in range(len(union_pos)):
            if union_pos[i] in data1_pos:
                ref.append(allREF[i])
                alt.append(allALT[i])
        joblib.dump(ref,pkl_ref)
        joblib.dump(alt,pkl_alt)