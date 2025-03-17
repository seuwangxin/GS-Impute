import subprocess
import os
import pandas as pd
import pycut.getFolder
import csv

#Getting the vcf subset with pos information
def getVcfByPos(vcf_path,vcfName,pos,panelPos,out,dirPath,chr,type='test'):
    pos_reader = open(pos, 'r+')
    pos_list=pos_reader.read().splitlines()
    pos_reader.close()

    panel_pos_reader = open(panelPos,'r+')
    panel_pos_list=panel_pos_reader.read().splitlines()
    panel_pos_reader.close()

    pos_list=pd.DataFrame(pos_list)
    panel_pos_list=pd.DataFrame(panel_pos_list)
    df=pd.concat([pos_list,panel_pos_list])
    del pos_list,panel_pos_list

    series=df.duplicated()

    del df
    panel_index_list=series[series.values==True].index 
    vcfRowList=[]
    headLineNum=0
    dataLineNum=0
    i=0
    if type=='test':
        path=dirPath+'/vcfOutput/'
        name=path+vcfName+'Chr'+str(chr)+'.vcf'
    else:
        name=vcf_path

    with open(name, encoding='utf-8-sig') as f:
        row=f.readline()
        while(row):
            if row[0][0] =='#':
                vcfRowList.append(row)
                headLineNum=headLineNum+1
            else:
                if dataLineNum == panel_index_list[i]:
                    vcfRowList.append(row)
                    i=i+1
                    if i ==len(panel_index_list):
                        break
                dataLineNum=dataLineNum+1
            row=f.readline()
    f.close()
    pycut.getFolder.mkdir(dirPath+'/vcfOutput')           
    vcfFile=open(dirPath+'/vcfOutput/'+out+'.vcf','w+')
    vcfFile.writelines(vcfRowList)
    vcfFile.close()
    del vcfRowList,panel_index_list

#Getting the vcf subset with chrom information
def getVcfByChr(vcf_path,vcfName,chr,dirPath):
    pycut.getFolder.mkdir(dirPath+'/vcfOutput')
    vcfRowList=[]
    chr_str=chr
    chr_int=True
    with open(vcf_path, encoding='utf-8-sig') as f:
        for row in csv.reader(f,delimiter='\n'):
            row1 = row.copy()
            if row1[0][0] =='#':
                vcfRowList.append(row1[0]+'\n')
            else:
                if chr_int:
                    if str(row1[0]).lower()[0:3] == 'chr':
                        chr_str=str(row1[0])[0:3]+str(chr)
                    else:
                        t_index = row1[0].find('\t')
                        if row1[0][0:t_index] == chr_str:
                            vcfRowList.append(row1[0] + '\n')
                    chr_int = False
                else:
                    t_index = row1[0].find('\t')
                    if row1[0][0:t_index] == chr_str:
                        vcfRowList.append(row1[0]+'\n')
    f.close()
    vcfFile=open(dirPath+'/vcfOutput/'+vcfName+'Chr'+str(chr)+'.vcf','w+')
    vcfFile.writelines(vcfRowList)
    vcfFile.close()
    del vcfRowList