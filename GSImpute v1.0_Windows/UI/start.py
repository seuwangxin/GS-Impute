#Start the menu
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from UI.Ui_RES2 import Ui_MainWindow as res_ui
from UI.Ui_IMP2 import Ui_MainWindow as imp_ui

class ImpWindow(QMainWindow,imp_ui): 
    def __init__(self,parent =None):
        super(ImpWindow,self).__init__(parent)
        self.setupUi(self)
    def switch(self):
        impWin.close()
        resWin.show()

class ResWindow(QMainWindow,res_ui): 
    def __init__(self,parent =None):
        super(ResWindow,self).__init__(parent)
        self.setupUi(self)
    def switch(self):
        resWin.close()
        impWin.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    impWin = ImpWindow() 
    resWin = ResWindow() 
    impWin.show()
    sys.exit(app.exec_())