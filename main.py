import sys, os, configparser
from tkinter.tix import ButtonBox
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QMenu, QMenuBar, QFileDialog, QTableWidget, QTableWidgetItem, QDialogButtonBox, QDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Fantasy Premier League"
        self.left = 0
        self.top = 0
        self.width = 800
        self.height = 800
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.mainWidget = MainWidget(self)
        self.setCentralWidget(self.mainWidget)
                
        self.createMenuBar()
        
        self.show()

    def createMenuBar(self):
        menuBar = QMenuBar(self)
        self.setMenuBar(menuBar)
        filemenu = QMenu("&File", self)
        filemenu.addAction("Load",self.onLoad)
        filemenu.addAction("Exit",self.onExit)
        menuBar.addMenu(filemenu)

    def onLoad(self):
        file , check = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()",
                                               "data", "Data Files (cringe-*.json);;")
        if check:
            print(file)
    def onExit(self):
        dialog = YesOrNoDialog()
        if dialog.exec():
            exit(0)
        else:
            pass

class YesOrNoDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Are you sure?")

        QButtons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QButtons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
    
class MainWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.myTeam = QWidget()
        self.playerStats = QWidget()
        self.teamStats = QWidget()
        self.tabs.resize(300,200)

        self.tabs.addTab(self.myTeam,"My Team")
        self.tabs.addTab(self.playerStats,"Player Stats")
        self.tabs.addTab(self.teamStats,"Team Stats")

        self.myTeam.layout = QVBoxLayout(self.myTeam)
        self.playerStats.layout = QVBoxLayout(self.playerStats)
        self.teamStats.layout = QVBoxLayout(self.teamStats)

        self.graphWidget = pg.PlotWidget()
        hour = [1,2,3,4,5,6,7,8]
        temperature = [30,32,34,32,33,31,29,32]
        self.graphWidget.plot(hour, temperature)

        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(4)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setItem(0,0, QTableWidgetItem("1"))
        self.tableWidget.setItem(0,1, QTableWidgetItem("2"))
        self.tableWidget.setItem(1,0, QTableWidgetItem("3"))
        self.tableWidget.setItem(1,1, QTableWidgetItem("4"))
        self.tableWidget.setItem(2,0, QTableWidgetItem("5"))
        self.tableWidget.setItem(2,1, QTableWidgetItem("6"))
        self.tableWidget.setItem(3,0, QTableWidgetItem("7"))
        self.tableWidget.setItem(3,1, QTableWidgetItem("8"))
        self.tableWidget.move(0,0)

        self.teamStats.layout.addWidget(self.graphWidget)
        self.teamStats.setLayout(self.teamStats.layout)
        
        self.playerStats.layout.addWidget(self.tableWidget)
        self.playerStats.setLayout(self.playerStats.layout)
        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())