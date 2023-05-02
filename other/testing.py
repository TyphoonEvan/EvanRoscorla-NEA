from lib2to3.pgen2 import driver
import sys, os, configparser
import json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt 
import pandas as pd
import ast

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
        self.setWindowIcon(QIcon("Icon.png"))

        self.layout = QVBoxLayout()

        self.layout1 = QVBoxLayout()
        self.layout2 = QVBoxLayout()
        self.layout3 = QVBoxLayout()
        self.mainLayout = QVBoxLayout()

        self.buttonsLayout = QHBoxLayout()
        self.button1 = QPushButton("Layout 1")
        self.button2 = QPushButton("Layout 2")
        self.button3 = QPushButton("Layout 3")

        self.button1.clicked.connect(self.setLayout1)
        self.button2.clicked.connect(self.setLayout2)
        self.button3.clicked.connect(self.setLayout3)

        self.mainLayout.addLayout(self.buttonsLayout)
        self.mainLayout.addLayout(self.layout1)
        self.layout.addLayout(self.mainLayout)
        self.show()

    def setLayout1(self):
        currentlayout = self.mainLayout.itemAt(1)
        self.mainLayout.removeItem(currentlayout)
        self.mainLayout.addLayout(self.layout1)

    def setLayout2(self):
        currentlayout = self.mainLayout.itemAt(1)
        self.mainLayout.removeItem(currentlayout)
        self.mainLayout.addLayout(self.layout2)

    def setLayout3(self):
        currentlayout = self.mainLayout.itemAt(1)
        self.mainLayout.removeItem(currentlayout)
        self.mainLayout.addLayout(self.layout3)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())