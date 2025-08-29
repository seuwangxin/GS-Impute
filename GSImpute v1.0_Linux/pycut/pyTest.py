import argparse
import pycut.getVcf
import pycut.getPos
import pycut.getFolder
import pycut.getPkl
import pycut.reconstructTask
import pycut.impute
import pycut.imputeTask

def main():
    parser = argparse.ArgumentParser()
    # parser.add_argument('-t', action='store_const', const=True, default=False, help='Testing')
    parser.add_argument('-r', action='store_const', const=True, default=False, help='Reconstructive imputation')
    parser.add_argument('-i', action='store_const', const=True, default=False, help='General imputation')
    
    parser.add_argument('-geno', nargs='?', type=str)
    parser.add_argument('-pos', nargs='?', type=str)
    parser.add_argument('-panel', nargs='?', type=str)
    parser.add_argument('-out', nargs='?', type=str)
    
    args = parser.parse_args()
    data1 = args.geno
    data2 = args.pos
    data = args.geno
    tem = args.panel
    out= args.out
    window_size=1000

    #Execute the task of reconstructive imputation
    if args.r:
        if (data1 is not None):
            data1=str(data1)
            data_A_path=data1
            data1Name = data1[0:-4]
        else:
            print("Error: Please select an unimputed genotype file (.vcf or .csv or .txt)!")
            return -1

        if (data2 is not None):
            data2 = str(data2)
            data_B_path=data2
            data2Name = data2[0:-4]
        else:
            print("Error: Please select a file with the columns Chr and Pos (.vcf or .csv or .txt)")
            return -1

        if (tem is not None):
            tem = str(tem)
            panel_path=tem
            temName=tem[0:-4]
        else:
            print("Error: Please select the reference panel file (.vcf)!")
            return -1
    
        dirPath = 'resTemp'
        pycut.getFolder.mkdir(dirPath)

        data1Type = data1[-3:]
        data2Type = data2[-3:]
        
        if (out is None):
            SavePath_and_SaveName='output.csv'
            SaveName='output'
            save_path=SavePath_and_SaveName
        else:
            SavePath_and_SaveName=str(out)
            SaveName=SavePath_and_SaveName.split('/')[-1]
            save_path=SavePath_and_SaveName+'.csv'

        
        print('Preprocessing (may take several minutes)')
        print("Getting positions")
        chr=pycut.getPos.getPosIndex(tem,temName, temName + 'pos', dirPath)
        if chr==-1:
            print('Error: No position records of the reference panel are detected!')
            return -1
        
        if (data1Type == 'vcf'):
            errorTest=pycut.getPos.getPosIndex(data_A_path, data1Name,str(data1Name) + 'pos', dirPath,chr)
            if errorTest==-1:
                print('Error: No position records of the genotype file are detected!')
                return -1

        elif (data1Type == 'csv' or data1Type == 'txt'):
            errorTest=pycut.getPos.getPosIndexByCsv(data_A_path, str(data1Name) + 'pos', dirPath,chr)
            if errorTest==-3:
                print('Error: No position records of the genotype file are detected!')
                return -1
            elif errorTest==-1:
                print('Error: The column chr of the genotype file is not found!')
                return -1
            elif errorTest==-2:
                print('Error: The column pos of the genotype file is not found!')
                return -1
        else:
            print("The input format of the genotype file is incorrect. Please select an unimputed genotype file (.vcf or .csv or .txt)!")
            return -1

        if (data2Type == 'vcf'):
             
             errorTest=pycut.getPos.getPosIndex(data_B_path, data2Name,str(data2Name) + 'pos', dirPath,chr)
             if errorTest==-1:
                print('Error: No position records of the genotype file are detected!')
                return -1
        elif (data2Type == 'csv' or data2Type =='txt'):
           
            errorTest=pycut.getPos.getPosIndexByCsv(data_B_path, str(data2Name) + 'pos', dirPath,chr)
            if errorTest==-3:
                print('Error: No position records of the genotype file are detected!')
                return -1
            elif errorTest==-1:
                print('Error: The column chr of the genotype file is not found!')
                return -1
            elif errorTest==-2:
                print('Error: The column pos of the genotype file is not found!')
                return -1
        else:
            print("Error: Please select a file with the columns Chr and Pos (.vcf or .csv)")
            return -1

        print("Getting the intersection of positions")
        errorTest=pycut.getPos.getIntersection(dirPath + '/postemp/' + data1Name + 'pos.txt',
                                     dirPath + '/postemp/' + temName + 'pos.txt', data1Name + '_templatePos', dirPath)
        if errorTest==-1:
            print('The number of marker intersection between the genotype file and the reference panel is zero!')
            return -1
        errorTest=pycut.getPos.getIntersection(dirPath + '/postemp/' + data2Name + 'pos.txt',
                                     dirPath + '/postemp/' + temName + 'pos.txt', data2Name + '_templatePos', dirPath)
        if errorTest==-1:
            print('The number of marker intersection between the position file and the reference panel is zero!')
            return -1
        
        if pycut.getPos.IntersectionLen<window_size and pycut.getPos.IntersectionLen>0:
            min_window_size=pycut.getPos.IntersectionLen
            if min_window_size%8==0:
                window_size=min_window_size
            else:
                window_size=(int(min_window_size/8))*8
            window_size=int(window_size)

        print("Getting the union of positions")
        pycut.getPos.getUnion(dirPath + '/postemp/' + data1Name + '_templatePos.txt',
                              dirPath + '/postemp/' + data2Name + '_templatePos.txt',
                              data1Name + '_' + data2Name + '_union', dirPath)
        print('Getting the actual panel file for training')
        pycut.getVcf.getVcfByPos(panel_path,
                                 temName, 
                                 dirPath + '/postemp/' + data1Name + '_' + data2Name + '_union.txt',
                                 dirPath + '/postemp/' +temName + 'pos.txt',
                                 data1Name + '_' + data2Name + '_union', dirPath,chr,'train')
        
        print('Segmenting the reference panel')
        subset_num = pycut.getPos.getUnionSubset(panel_path,temName, data1Name + '_' + data2Name , dirPath,window_size,chr)
        train_loop_num=pycut.getPos.getLoopNum(data1Name + '_' + data2Name + '_union.txt', dirPath,window_size)
        print('Segmenting the genotype files')
        pycut.getPos.getIntersectionSubset(data1Name, subset_num, dirPath)
        pycut.getPos.getIntersectionSubset(data2Name, subset_num, dirPath)
        if (data1Type == 'vcf'):
            pycut.getVcf.getVcfByPos(data_A_path,data1Name, 
                                        dirPath + '/postemp/' + data1Name + '_templatePos.txt',
                                        dirPath + '/postemp/' +data1Name + 'pos.txt',
                                        data1Name + '_subset', dirPath,chr)
        print('Reading the genotype data')
        pycut.getPkl.getResRefAndAlt(data1Name,data2Name,subset_num,dirPath)
        if (data1Type == 'vcf'):
            pycut.getPos.getVcfSubset(data_A_path,data1Name,subset_num,dirPath,chr)
        elif (data1Type == 'csv' or data1Type =='txt'):
            csvData=pycut.getPkl.getPklByCsvFenduan(data_A_path,data1Name, dirPath, subset_num,chr)
            if(csvData==-1):
                print('Error: Format of the target genotype file is unexpected!')
                return -1
        
        print('Training in progress')
        pycut.reconstructTask.Restructure(data1Name,data1Type, data2Name, dirPath, subset_num,train_loop_num,window_size)
        print('\n')
        print('Merging and saving the imputation results (may take several minutes)')
        pycut.getPkl.mergePkl(subset_num, data1Name, dirPath,'RES')
        pycut.impute.Impute(data1Name, 'RES', dirPath,subset_num)
        print('Saving the imputation results')
        pycut.reconstructTask.RESgetCsv(data_A_path,data1Name,data1Type, data2Name, dirPath,SaveName,subset_num,save_path)
        print('Completed')
        pycut.getFolder.delete_local_dir(dirPath)

    #Execute the task of general impute 
    if args.i:
        if (data is not None):
            data=str(data)
            data_A_path=data
            dataName = data[0:-4]
        else:
            print("Error: Please select an unimputed genotype file (.vcf or .csv)!")
            return -1
        
        if (tem is not None):
            tem = str(tem)
            panel_path=tem
            temName=tem[0:-4]
        else:
            print("Error: Please select the reference panel file (.vcf)!")
            return -1

        dirPath = 'impTemp'
        pycut.getFolder.mkdir(dirPath)
        dataType = data[-3:]
        if (out is None):
            SaveName='output'
            save_path='output.'+dataType
        else:
            SavePath_and_SaveName=str(out)
            SaveName=SavePath_and_SaveName.split('/')[-1]
            save_path=str(out)+'.'+dataType

        print('Preprocessing (may take several minutes)')
        print("Getting positions of loci")
        chr=pycut.getPos.getPosIndex(panel_path,temName, temName + 'pos', dirPath)
        if chr==-1:
            print('Error: No position records of the reference panel are detected!')
            return -1
        if (dataType == 'vcf'):
            errorTest=pycut.getPos.getPosIndex(data_A_path,dataName, str(dataName) + 'pos', dirPath,chr)
            if errorTest==-1:
                print('Error: No position records of the genotype file are detected!')
                return -1
        elif (dataType == 'csv' or dataType == 'txt'):
            errorTest=pycut.getPos.getPosIndexByCsv(data_A_path, str(dataName) + 'pos', dirPath,chr)
            if errorTest==-3:
                print('Error: No position records of the genotype file are detected!')
                return -1
            elif errorTest==-1:
                print('Error: The column Chr of the genotype file is not found!')
                return -1
            elif errorTest==-2:
                print('Error: The column Pos of the genotype file is not found!')
                return -1
        else:
            print("The input format of the genotype file is incorrect, please select an unimputed genotype file (.vcf or .csv or .txt)!")
            return -1

        print("Getting the intersection of positions")
        errorTest=pycut.getPos.getIntersection(dirPath + '/postemp/' + dataName + 'pos.txt',
                                     dirPath + '/postemp/' + temName + 'pos.txt', dataName + '_templatePos', dirPath)
        if errorTest==-1:
            print('The number of marker intersection between the genotype file and the reference panel is zero!')
            return -1

        if pycut.getPos.IntersectionLen<window_size and pycut.getPos.IntersectionLen>0:
            min_window_size=pycut.getPos.IntersectionLen
            if min_window_size%8==0:
                window_size=min_window_size
            else:
                window_size=(int(min_window_size/8))*8
            window_size=int(window_size)

        print("Getting the actual panel file for training")
        pycut.getVcf.getVcfByPos(panel_path,temName, 
                                 dirPath + '/postemp/' + dataName + '_templatePos.txt', 
                                 dirPath + '/postemp/' +temName + 'pos.txt',
                                 dataName + '_train', 
                                 dirPath,chr,'train')
        print("Segmenting the panel")
        subset_num = pycut.getPos.getTrainSubset(panel_path,temName, dataName , dirPath,window_size,chr)
        train_loop_num=pycut.getPos.getLoopNum(dataName + '_templatePos.txt', dirPath,window_size)
        print('Segmenting the genotype files')
        pycut.getPos.getIntersectionSubset2(dataName, subset_num, dirPath)
    
        if (dataType == 'vcf'):
            pycut.getVcf.getVcfByPos(data_A_path,dataName, 
                                     dirPath + '/postemp/' + dataName + '_templatePos.txt' , 
                                     dirPath + '/postemp/' +dataName + 'pos.txt',
                                     dataName + '_subset', dirPath,chr)
        print('Reading the genotype data')
        pycut.getPkl.getPklByvcf(dataName + '_train.vcf', 0,dirPath)

        if (dataType == 'vcf'):
            pycut.getPos.getVcfSubset(data_A_path,dataName,subset_num,dirPath,chr)
        elif (dataType == 'csv' or dataType == 'txt'):
            csvData=pycut.getPkl.getPklByCsvFenduan(data_A_path,dataName, dirPath, subset_num,chr)
            if(csvData==-1):
                print('Format of the target genotype file is unexpected!')
                return 301
        else:
            print("No input data!")
        print('Training in progress')
        k=pycut.imputeTask.ImputeTask(dataName,dataType,subset_num,train_loop_num,window_size,dirPath)
        if k ==-1:
            print("There are no missing loci detected, and imputation is unnecessary.")
            return 401

        print('\n')
        print('Saving the imputation results (may take several minutes)')
        if dataType == 'csv' or dataType == 'txt' :
            pycut.reconstructTask.IMPgetTxtOrCsv(data_A_path,dataName,dataType, dirPath,SaveName,chr,subset_num,save_path)
        else:
            pycut.reconstructTask.IMPgetVcf(dataName,dirPath,SaveName,subset_num,save_path)
        pycut.getFolder.delete_local_dir(dirPath)
        print('Completed')

if __name__ == '__main__':
    main()
