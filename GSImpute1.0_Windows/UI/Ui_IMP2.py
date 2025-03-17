from threading import Thread
import threading
import time
import tkinter
import tracemalloc
import typing
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import torch
from UI.IMP import to_IMP
import UI.IMP
import gc
gc.set_threshold(700, 10, 5)
global task_start
task_start=0

class myThread(QThread):
    task_Signal = pyqtSignal(str)
    task_state_Signal=pyqtSignal(int,str)
    pro_Signal = pyqtSignal(float,float,float,str,int)
    task_list_Signal = pyqtSignal(str)
    task_error_Signal = pyqtSignal(str)
    task_warning_Signal = pyqtSignal(str)

    def __init__(self,i,data_A_path,panel_path,dirPath, parent=None):
        super().__init__(parent)
        self.i=i
        self.data_A_path=data_A_path
        self.panel_path=panel_path
        self.dirPath=dirPath
        
    def run(self):
        global task_start
        task_start=1
        to_IMP(self,self.i,self.data_A_path,self.panel_path,self.dirPath)
        gc.collect()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(977, 682)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(180, 30, 561, 27))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)
        self.textEdit.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.textEdit.setObjectName("textEdit")
        self.pushButton_A = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_A.setGeometry(QtCore.QRect(780, 30, 121, 31))
        self.pushButton_A.setObjectName("pushButton_A")
        self.pushButton_panel = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_panel.setGeometry(QtCore.QRect(780, 75, 121, 31))
        self.pushButton_panel.setObjectName("pushButton_panel")
        self.textEdit_3 = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_3.setGeometry(QtCore.QRect(180, 75, 561, 27))
        self.textEdit_3.setObjectName("textEdit_3")
        self.pushButton_path = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_path.setGeometry(QtCore.QRect(780, 120, 121, 31))
        self.pushButton_path.setObjectName("pushButton_path")
        self.textEdit_4 = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_4.setGeometry(QtCore.QRect(180, 120, 561, 27))
        self.textEdit_4.setObjectName("textEdit_4")
        self.pushButton_add = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_add.setGeometry(QtCore.QRect(40, 190, 141, 31))
        self.pushButton_add.setObjectName("pushButton_add")
        self.pushButton_imp = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_imp.setGeometry(QtCore.QRect(370, 190, 141, 31))
        self.pushButton_imp.setObjectName("pushButton_imp")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(30, 260, 621, 331))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(125)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(30, 610, 891, 23))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressBar.sizePolicy().hasHeightForWidth())
        self.progressBar.setSizePolicy(sizePolicy)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.task_log = QtWidgets.QTextBrowser(self.centralwidget)
        self.task_log.setGeometry(QtCore.QRect(680, 260, 241, 331))
        self.task_log.setPlaceholderText("")
        self.task_log.setObjectName("task_log")
        self.pushButton_clear = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_clear.setGeometry(QtCore.QRect(820, 230, 101, 23))
        self.pushButton_clear.setObjectName("pushButton_clear")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(680, 230, 91, 21))
        font = QtGui.QFont()
        font.setFamily("Adobe Heiti Std")
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(-30, 35, 201, 20))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(-60, 125, 231, 20))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(10, 80, 161, 20))
        self.label_4.setObjectName("label_4")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 977, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        self.actional_res = QtWidgets.QWidgetAction(self.statusbar)
        self.actional_res.setObjectName('RES_actional')
        self.actional_res.setText("Reconstructive Imputation")

        self.actional_imp = QtWidgets.QWidgetAction(self.statusbar)
        self.actional_imp.setObjectName('IMP_actional')
        self.actional_imp.setText("General Imputation")
       
        self.menubar.addAction(self.actional_res)
        self.menubar.addAction(self.actional_imp)

        self.menuBar().setStyleSheet('QMenuBar{background-color:white;} QMenuBar::item {background-color:white;} QMenuBar::item:disabled{Background: rgb(240,240,240);}')
        
        self.actional_imp.setEnabled(False)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.actional_res.triggered.connect(MainWindow.switch)
        self.tableWidget.horizontalHeader().setStyleSheet("border:1px solid rgb(210, 210, 210);")
        self.progressBar.hide()
        
        if torch.cuda.is_available():
            pass
        else:
            self.task_log.append('The system failed to detect any GPUs. It is recommended to configure at least one GPU to accelerate your program.')
        self.pushButton_imp.setToolTip('Execute the tasks below')
        MainWindow.setFixedSize(MainWindow.width(), MainWindow.height())

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "GS-Impute 1.0"))
        self.textEdit.setPlaceholderText(_translate("MainWindow", "Please select an unimputed genotype file (.vcf or .csv or .txt)"))
        self.pushButton_A.setText(_translate("MainWindow", "Browse"))
        self.pushButton_panel.setText(_translate("MainWindow", "Browse"))
        self.textEdit_3.setPlaceholderText(_translate("MainWindow", "Please select the reference panel file (.vcf)"))
        self.pushButton_path.setText(_translate("MainWindow", "Browse"))
        self.textEdit_4.setPlaceholderText(_translate("MainWindow", "Please select the output name and the saving path"))
        self.pushButton_add.setText(_translate("MainWindow", "Add task"))
        self.pushButton_imp.setText(_translate("MainWindow", "Run"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Genotype file"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Reference panel"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Output file"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Task state"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Remove"))
        self.pushButton_clear.setText(_translate("MainWindow", "Clear Log"))
        self.label.setText(_translate("MainWindow", "Task Log"))
        self.label_2.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\"><span style=\" font-size:10pt; font-weight:600;\">Genotype file</span></p></body></html>"))
        self.label_3.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\"><span style=\" font-size:10pt; font-weight:600;\">Output file path</span></p></body></html>"))
        self.label_4.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\"><span style=\" font-size:10pt; font-weight:600;\">Reference panel</span></p></body></html>"))

    @pyqtSlot()
    def on_pushButton_A_clicked(self):
        data_A_path1,_=QFileDialog.getOpenFileName(self,filter='Genotype File(*.vcf *.csv *.txt)')
        data_A_path= '\\'.join(data_A_path1.split('/'))
        self.textEdit.setPlainText(data_A_path)
        fileType=data_A_path1.split('/')[-1][-3:]
        save_path_list=data_A_path1.split('/')[0:-1]
        rowNum = self.tableWidget.rowCount()
        save_path_list.append('output_'+str(rowNum+1)+'.'+str(fileType))
        save_path='\\'.join(save_path_list)
        if data_A_path1=='':
            self.textEdit_4.setPlainText('')
        else:
            self.textEdit_4.setPlainText(save_path)

    @pyqtSlot()
    def on_pushButton_panel_clicked(self):
        pre_Panel_path=self.textEdit_3.toPlainText()
        pre_Panel_path= '\\'.join(pre_Panel_path.split('/'))
        if pre_Panel_path=='':
            panel_path1,_=QFileDialog.getOpenFileName(self,filter='Variant Call Format(*.vcf)')
        else:
            panel_path1,_=QFileDialog.getOpenFileName(self,directory=pre_Panel_path,filter='Variant Call Format(*.vcf)')

        panel_path= '\\'.join(panel_path1.split('/'))
        self.textEdit_3.setPlainText(panel_path)
    
    @pyqtSlot()
    def on_pushButton_path_clicked(self):
        if(self.textEdit.toPlainText() == ''):
            QMessageBox.warning(None, "Warning", "Please select the target genotype file before selecting the saving path!")
        else:
            getData_A=self.textEdit.toPlainText()
            save_path=getData_A.split('\\')[0:-1]
            defalt_save_path='\\'.join(save_path)
            fileType=getData_A.split('/')[-1][-3:]
            rowNum = self.tableWidget.rowCount()
            dir_path1,type=QFileDialog.getSaveFileName(self,'Select the saving path and the file name',defalt_save_path+'\\'+'output_'+str(rowNum+1)+'.'+str(fileType),str(fileType)+'(*.'+str(fileType)+')')
            dir_path= '\\'.join(dir_path1.split('/'))
            self.textEdit_4.setPlainText(dir_path)

    @pyqtSlot()
    def on_pushButton_imp_clicked(self):
        self.actional_imp.setEnabled(False)
        self.actional_res.setEnabled(False)
        self.pushButton_imp.setEnabled(False)
        self.pushButton_add.setEnabled(False)
        self.tableWidget.setAutoFillBackground(True)
        self.tableWidget.setBackgroundRole(QPalette.Base)
        p = self.tableWidget.palette()
        p.setColor(self.tableWidget.backgroundRole(), Qt.gray)
        self.tableWidget.setPalette(p)
        QApplication.processEvents()
        
        self.row_num = self.tableWidget.rowCount()
        self.threads=[]
        for i in range(self.row_num):
            if self.tableWidget.item(i,3).text() != 'Completed' and self.tableWidget.item(i,3).text() != 'Task Error':
                self.data_A_path=self.tableWidget.item(i,0).text()
                self.panel_path=self.tableWidget.item(i,1).text()
                self.dirPath=self.tableWidget.item(i,2).text()
                self.thread = myThread(i,self.data_A_path,self.panel_path,self.dirPath)
                self.threads.append(self.thread)
        if len(self.threads)==0:
            self.tableWidget.setBackgroundRole(QPalette.Base)
            p = self.tableWidget.palette()
            p.setColor(self.tableWidget.backgroundRole(), Qt.white)
            self.tableWidget.setPalette(p)
            self.pushButton_imp.setEnabled(True)
            self.pushButton_add.setEnabled(True)
            self.actional_res.setEnabled(True)
            global task_start
            task_start=0
            QMessageBox.warning(None, "Warning", "There are no tasks waiting to be executed!")
        else:
            time.sleep(0.05)
            for i in self.threads:
                gc.collect()
                i.task_state_Signal.connect(self.task_state_update,type=Qt.BlockingQueuedConnection)
                i.task_Signal.connect(self.task_Test,type=Qt.BlockingQueuedConnection)
                i.pro_Signal.connect(self.pro_Test,type=Qt.BlockingQueuedConnection)
                i.task_list_Signal.connect(self.add_task_list,type=Qt.BlockingQueuedConnection)
                i.task_error_Signal.connect(self.show_error,type=Qt.BlockingQueuedConnection)
                i.task_warning_Signal.connect(self.show_warning,type=Qt.BlockingQueuedConnection)
                i.start()
                time.sleep(0.2)

    @pyqtSlot()
    def on_pushButton_add_clicked(self):
        if(self.textEdit.toPlainText() == ''):
            QMessageBox.warning(None, "Warning", "Please select an unimputed genotype file! (.vcf or .csv or .txt)")
        elif self.textEdit_3.toPlainText()== '':
            QMessageBox.warning(None, "Warning", "Please select the reference panel file! (.vcf)")
        elif self.textEdit_4.toPlainText()== '':
            QMessageBox.warning(None, "Warning", "Please select the output name and the saving path!")
        else:
            getData_A=self.textEdit.toPlainText()
            getData_panel=self.textEdit_3.toPlainText()
            getData_dirPath=self.textEdit_4.toPlainText()
            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)
            self.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(getData_A))
            self.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(getData_panel))
            self.tableWidget.setItem(rowPosition, 2, QTableWidgetItem(getData_dirPath))
            self.tableWidget.setItem(rowPosition, 3, QTableWidgetItem('Unexecuted'))
            self.tableWidget.setItem(rowPosition, 4, QTableWidgetItem('Remove'))
            self.tableWidget.resizeColumnsToContents()
            self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
            self.textEdit_4.setPlainText('')
    
    @pyqtSlot(int,int)
    def on_tableWidget_cellClicked(self,currentRow, currentColumn):
        if task_start==0:
            if currentColumn == 4 and currentRow != -1:
                self.tableWidget.removeRow(currentRow)
    
    @pyqtSlot()
    def on_pushButton_clear_clicked(self):
       self.task_log.clear()
    
    def task_Test(self,string):
        pass
    
    def pro_Test(self,v,epoch,all_epoch,msg,task_num):
        self.progressBar.setValue(v)
        if epoch == 0 and all_epoch==0:
            self.progressBar.setFormat('No tasks conducted')
        else:
            self.progressBar.setFormat('Current progress of task '+str(task_num)+': '+str(v)+'% ('+str(int(epoch))+'/'+str(int(all_epoch))+' epochs)')
            if(v==100):
                self.progressBar.setFormat(msg)
        self.progressBar.setAlignment(Qt.AlignCenter)
    
    def task_state_update(self,task_num,string):
        if string =='Preprocessing':
            self.progressBar.show()
            self.progressBar.setFormat('Task '+str(task_num)+': Preprocessing (may take several minutes)')
        self.tableWidget.setItem(task_num-1, 3, QTableWidgetItem(string))
        if string =='Completed' or string =='Task Error' :
            self.progressBar.hide()
            for i in range(5):
                data=self.tableWidget.item(task_num-1,i).text()
                newItem=QTableWidgetItem(data)
                if string=='Task Error' and i == 3:
                    newItem.setForeground(QtGui.QColor(255,0,0))
                newItem.setBackground(QtGui.QColor(169,169,169))
                self.tableWidget.setItem(task_num-1, i, newItem)
        self.tableWidget.resizeColumnsToContents()
        row_num = self.tableWidget.rowCount()
        print(row_num)
        global task_start
        completed_task_num=0
        all_completed=0
        for i in range(row_num):
           if self.tableWidget.item(i,3).text() == 'Completed' or self.tableWidget.item(i,3).text() == 'Task Error':
                completed_task_num=completed_task_num+1
        if completed_task_num == row_num:
            all_completed=1
        if all_completed==1:
            self.tableWidget.setBackgroundRole(QPalette.Base)
            p = self.tableWidget.palette()
            p.setColor(self.tableWidget.backgroundRole(), Qt.white)
            self.tableWidget.setPalette(p)
            self.pushButton_imp.setEnabled(True)
            self.pushButton_add.setEnabled(True)
            self.actional_res.setEnabled(True)
            gc.collect()
            task_start=0
    
    def add_task_list(self,task_msg):
        self.task_log.append(task_msg)
        self.task_log.moveCursor(self.task_log.textCursor().End)
        self.task_log.ensureCursorVisible()
    
    def show_error(self,error_msg):
        QMessageBox.warning(None, "Warning", error_msg)
    
    def show_warning(self,error_msg):
        api=QMessageBox.question(self,"Warning",error_msg,QMessageBox.Yes | QMessageBox.No,QMessageBox.No)
        if api==QMessageBox.Yes:
            UI.IMP.task_P=1
        else:
            UI.IMP.task_P=-1