from lib2to3.pgen2 import driver
import sys, os, configparser
import json
from turtle import forward
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QTabWidget, QVBoxLayout, QMenu, QMenuBar, QFileDialog, QDialogButtonBox, QDialog, QGridLayout, QGroupBox, QComboBox, QTableView, QLabel, QInputDialog, QLineEdit
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import pyqtSlot, Qt, QAbstractTableModel
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
from download import downloader
import pandas as pd
import requests
from datetime import date
from algorithms.pointsprediction import *
from cryptography.fernet import Fernet
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
        loginmenu = QMenu("&Login", self)
        loginmenu.addAction("Login", self.onLogin)
        loginmenu.addAction("Create Account", self.onCreateAccount)
        menuBar.addMenu(filemenu)

    def onLoad(self):
        file , check = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()",
                                               "config", "Data Files (*.cnfg);;")
        if check:
            file = open(file, "rb")
            data = file.read()
            data = f.decrypt(data)
            data = ast.literal_eval(data.decode("utf-8"))
            passwordentered, done = QInputDialog.getText(self, 'Input Dialog', 'Enter your password:')
            if passwordentered == data["password"]:
                return data
    def onExit(self):
        dialog = YesOrNoDialog()
        if dialog.exec():
            exit(0)
        else:
            pass
    
    def onLogin(self):
        dialog = Login()
        data = dialog.exec()
    def onCreateAccount(self):
        dialog = CreateAccount()
        dialog.exec()

class Login(QDialog):
    def __init__(self):
        super().__init__()
        self.width = 400
        self.height = 240
        self.namelabel = QLabel(self)
        self.namelabel.setText("Name:")
        self.nameline = QLineEdit(self)
        self.nameline.move(80, 20)
        self.nameline.resize(200, 32)
        self.namelabel.move(20, 20)
        self.passwordlabel = QLabel(self)
        self.passwordlabel.setText("Password:")
        self.passwordline = QLineEdit(self)
        self.passwordline.move(80, 80)
        self.passwordline.resize(200, 32)
        self.passwordlabel.move(20, 80)
        self.button = QPushButton("Login", self)
        self.button.move(20,200)
        data = self.button.clicked.connect(self.login)
        self.show()
        return data
    
    @pyqtSlot()
    def login(self):
        file = open("config\\"+self.nameline.text()+".cnfg")
        data = file.read()
        data = f.decrypt(data).decode("utf-8")
        data = ast.literal_eval(data)
        file.close()
        print(data.get("password"))
        if self.passwordline.text() == data.get("password"):
            return data
        else:
            return -1

class CreateAccount(QDialog):
    def __init__(self):
        super().__init__()

        self.width = 400
        self.height = 240

        self.namelabel = QLabel(self)
        self.namelabel.setText("Name:")
        self.nameline = QLineEdit(self)

        self.nameline.move(80, 20)
        self.nameline.resize(200, 32)
        self.namelabel.move(20, 20)

        self.passwordlabel = QLabel(self)
        self.passwordlabel.setText("Password:")
        self.passwordline = QLineEdit(self)

        self.passwordline.move(80, 80)
        self.passwordline.resize(200, 32)
        self.passwordlabel.move(20, 80)

        self.idlabel = QLabel(self)
        self.idlabel.setText("ID:")
        self.idline = QLineEdit(self)

        self.idline.move(80, 140)
        self.idline.resize(200, 32)
        self.idlabel.move(20, 140)

        self.button = QPushButton("Create account", self)
        self.button.move(20,200)
        
        self.button.clicked.connect(self.create)
        self.show()

    @pyqtSlot()
    def create(self):
        user = {"name": self.nameline.text(), "password": self.passwordline.text(), "manager_id": self.idline.text()}
        user = f.encrypt(str(user).encode("utf-8"))
        filename = "config\\"+self.nameline.text()+".cnfg"
        file = open(filename, "wb")
        file.write(user)
        file.close()

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

class pandasModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None
    
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

        teamdict = downloader.AutoDownloader.getUserData("evan")

        self.myTeam.layout = QVBoxLayout(self.myTeam)
        self.playerStats.layout = QVBoxLayout(self.playerStats)
        self.teamStats.layout = QVBoxLayout(self.teamStats)

        file = open("data\\bootstrap-static.json", "rb")
        data = file.read()
        data = json.loads(data)
        playersframe = pd.DataFrame(data["elements"])
        playersubframe = playersframe[["first_name", "second_name", "code", "team", "id", "total_points", "goals_scored", "assists", "minutes", "points_per_game", "saves", "clean_sheets", "ict_index", "influence", "creativity", "threat", "now_cost"]]
        self.dataframe = playersubframe.sort_values("id")

        file = open("data\\goals_scored.json", "r")
        data = file.read()
        goals_scored = pd.read_json(data)
        file.close()

        file = open("data\\assists.json", "r")
        data = file.read()
        assists = pd.read_json(data)
        file.close()

        file = open("data\\points.json", "r")
        data = file.read()
        points = pd.read_json(data)
        file.close()

        file = open("data\\saves.json", "r")
        data = file.read()
        saves = pd.read_json(data)
        file.close()

        file = open("data\\clean_sheets.json", "r")
        data = file.read()
        clean_sheets = pd.read_json(data)
        file.close()
        self.dataframe = pd.concat([self.dataframe, goals_scored, assists, points, saves, clean_sheets], axis=1)
        self.dataframe = self.dataframe.loc[:,~self.dataframe.columns.duplicated(keep="first")].copy()

        self.tempframe = self.dataframe
        self.firstnames = self.dataframe["first_name"].to_list()
        self.secondnames = self.dataframe["second_name"].to_list()
        self.prices = self.dataframe["now_cost"].to_list()
        self.ids = self.dataframe["id"].to_list()
        self.fullnames = []
        for i in range(len(self.firstnames)):
            self.fullnames.append(self.firstnames[i] + " " + self.secondnames[i])
        self.namesandprices = []
        for i in range(len(self.fullnames)):
            currentdict = {"name": self.fullnames[i], "price": self.prices[i]}
            self.namesandprices.append(currentdict)

        self.sortSelector = QComboBox()
        items = ["Alphabetical", "Total Points", "Points Per Game"]
        self.sortSelector.addItems(items)
        self.sortSelector.currentIndexChanged.connect(self.setOrder)

        self.resetButton = QPushButton("Reset")
        self.resetButton.clicked.connect(self.reset)

        self.teamLayout = QGroupBox("My Team")
        layout = QGridLayout()
        #creates dropdown
        self.forward1 = QComboBox()
        self.forward2 = QComboBox()
        self.midfielder1 = QComboBox()
        self.midfielder2 = QComboBox()
        self.midfielder3 = QComboBox()
        self.defender1 = QComboBox()
        self.defender2 = QComboBox()
        self.defender3 = QComboBox()
        self.defender4 = QComboBox()
        self.defender5 = QComboBox()
        self.goalkeeper = QComboBox()
        #adds dropdowns to tab
        layout.addWidget(self.forward1,0,1)
        layout.addWidget(self.forward2,0,3)
        layout.addWidget(self.midfielder1,1,1)
        layout.addWidget(self.midfielder2,1,2)
        layout.addWidget(self.midfielder3,1,3)
        layout.addWidget(self.defender1,2,0)
        layout.addWidget(self.defender2,2,1)
        layout.addWidget(self.defender3,2,2)
        layout.addWidget(self.defender4,2,3)
        layout.addWidget(self.defender5,2,4)
        layout.addWidget(self.goalkeeper,3,2)

        self.setPlayerTeam()
        self.priceUpdate()
        
        self.teamLayout.setLayout(layout)
        self.createPlayerTable()

        self.myTeam.layout.addWidget(self.teamLayout)
        self.myTeam.layout.addWidget(self.sortSelector)
        self.myTeam.layout.addWidget(self.resetButton)
        self.myTeam.setLayout(self.myTeam.layout)
        self.playerStats.layout.addWidget(self.playerslayout)
        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def setOrder(self, type):
        if type == 0:
            dataframe = self.tempframe.sort_values("second_name")
        elif type == 1:
            dataframe = self.tempframe.sort_values("total_points")
        elif type == 2:
            dataframe = self.tempframe.sort_values("points_per_game")
        self.dataframe = dataframe
        self.populateDropDowns()

    def getCurrentGameweek(gameweeks):
        for i in range(len(gameweeks.index)):
            if gameweeks.iloc[i, 4] == "true":
                return i+1

    def populateDropDowns(self):
        self.goalkeepers = self.createPlayerLists(1, False)#creates the list of players
        self.goalkeeper.clear()#clears current dropdown
        self.goalkeeper.addItems(self.goalkeepers)#adds the new list to the dropdown
        self.defenders = self.createPlayerLists(2, False)
        self.defender1.clear()
        self.defender2.clear()
        self.defender3.clear()
        self.defender4.clear()
        self.defender5.clear()
        self.defender1.addItems(self.defenders)
        self.defender2.addItems(self.defenders)
        self.defender3.addItems(self.defenders)
        self.defender4.addItems(self.defenders)
        self.defender5.addItems(self.defenders)
        self.midfielders = self.createPlayerLists(3, False)
        self.midfielder1.clear()
        self.midfielder2.clear()
        self.midfielder3.clear()
        self.midfielder1.addItems(self.midfielders)
        self.midfielder2.addItems(self.midfielders)
        self.midfielder3.addItems(self.midfielders)
        self.attackers = self.createPlayerLists(4, False)
        self.forward1.clear()
        self.forward2.clear()
        self.forward1.addItems(self.attackers)
        self.forward2.addItems(self.attackers)
        self.priceUpdate()
        self.sortSelector.update()

    def createPlayerLists(self, typenum, isplayerteam):
        if isplayerteam == True:
            currentplayer = self.tempframe[self.tempframe["id"]==self.currentid]#gets player from the main dataframe
            currentfirstname = currentplayer.iloc[0, 12]#gets first name
            currentsecondname = currentplayer.iloc[0, 21]#gets first name
            currentname = currentfirstname + " " + currentsecondname
        self.playersframe = self.tempframe[self.tempframe["element_type"]==typenum]#gets all players in a position
        playersfirstname = self.playersframe["first_name"].to_list()
        playerssecondname = self.playersframe["second_name"].to_list()
        self.players = []
        for i in range(len(playersfirstname)):
            self.players.append(playersfirstname[i] + " " + playerssecondname[i])#adds first and last names together
        if isplayerteam == True:
            playerpos = self.players.index(currentname)#finds player position in list
            self.players.pop(playerpos)#removes player from list
            self.players.insert(0, currentname)#adds player to first position
        return self.players

    def createPlayerTable(self):
        dataframe = self.dataframe
        tableframe = dataframe[["first_name", 
        "second_name", 
        "total_points", 
        "points_per_game", 
        "yellow_cards", 
        "red_cards", 
        "goals_scored", 
        "assists", 
        "goals_conceded", 
        "saves"]]
        self.playerslayout = QTableView()
        playertable = pandasModel(tableframe)
        self.playerslayout.setModel(playertable)

    def reset(self):
        self.setPlayerTeam()

    def priceUpdate(self):
        maxprice = 1000
        totalcost = 0
        dropdownslist = [self.goalkeeper, self.defender1, self.defender2, self.defender3, self.defender4, self.defender5, self.midfielder1, self.midfielder2, self.midfielder3, self.forward1, self.forward2]
        for i in range(11):
            currentdropdown = dropdownslist[i]
            currentplayer = str(currentdropdown.currentText())
            for i in range(len(self.namesandprices)):
                if currentplayer == self.namesandprices[i]["name"]:
                    cost = self.namesandprices[i]["price"]
                    break
            totalcost-=cost
        remainingmoney = maxprice-totalcost
        for i in range(11):
            self.tempframe = self.dataframe
            for x in range(len(self.tempframe)):
                if self.tempframe.iloc[x,18] > remainingmoney:
                    self.tempframe.drop(self.tempframe.index[x])

    def setPlayerTeam(self):
        self.dataframe = self.dataframe.sort_values("second_name")
        idslist = self.teamdict["element"]
        self.currentid = idslist[0]#gets goalkeeper id
        self.goalkeepers = self.createPlayerLists(1, True)#creates the list of players
        self.goalkeeper.clear()#clears current dropdown
        self.goalkeeper.addItems(self.goalkeepers)#adds the new list to the dropdown
        self.currentid = idslist[1]
        self.defenders = self.createPlayerLists(2, True)
        self.defender1.clear()
        self.defender1.addItems(self.defenders)
        self.currentid = idslist[2]
        self.defenders = self.createPlayerLists(2, True)
        self.defender2.clear()
        self.defender2.addItems(self.defenders)
        self.currentid = idslist[3]
        self.defenders = self.createPlayerLists(2, True)
        self.defender3.clear()
        self.defender3.addItems(self.defenders)
        self.currentid = idslist[4]
        self.defenders = self.createPlayerLists(2, True)
        self.defender4.clear()
        self.defender4.addItems(self.defenders)
        self.currentid = idslist[5]
        self.defenders = self.createPlayerLists(2, True)
        self.defender5.clear()
        self.defender5.addItems(self.defenders)
        self.currentid = idslist[6]
        self.midfielders = self.createPlayerLists(3, True)
        self.midfielder1.clear()
        self.midfielder1.addItems(self.midfielders)
        self.currentid = idslist[7]
        self.midfielders = self.createPlayerLists(3, True)
        self.midfielder2.clear()
        self.midfielder2.addItems(self.midfielders)
        self.currentid = idslist[8]
        self.midfielders = self.createPlayerLists(3, True)
        self.midfielder3.clear()
        self.midfielder3.addItems(self.midfielders)
        self.currentid = idslist[9]
        self.attackers = self.createPlayerLists(4, True)
        self.forward1.clear()
        self.forward1.addItems(self.attackers)
        self.currentid = idslist[10]
        self.attackers = self.createPlayerLists(4, True)
        self.forward2.clear()
        self.forward2.addItems(self.attackers)
        self.priceUpdate()
        self.sortSelector.update()
        
def onStart():
    file = open("data\\bootstrap-static.json", "rb")
    data = file.read()
    data = json.loads(data)
    gameweeks = pd.DataFrame(data["events"])
    gameweek = getCurrentGameweek(gameweeks)
    file.close()
    downloader.AutoDownloader.downloadGenericData(gameweek)
    playersframe = downloader.AutoDownloader.getPlayersFrame()
    teamsframe = downloader.AutoDownloader.getTeamsFrame()
    return playersframe, teamsframe

if __name__ == '__main__':
    playersframe, teamsframe = onStart()
    file = open("key.key", "rb")
    key = file.read()
    file.close()
    f = Fernet(key)
    app = QApplication(sys.argv)
    ex = App() 
    sys.exit(app.exec_())