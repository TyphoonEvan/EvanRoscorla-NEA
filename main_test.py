from lib2to3.pgen2 import driver
import sys, os, configparser
import json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot, Qt, QAbstractTableModel
from download import downloader
import pandas as pd
from algorithms.pointsprediction import *
from cryptography.fernet import Fernet
import ast
import requests

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

        menuBar = QMenuBar(self)
        self.setMenuBar(menuBar)
        filemenu = QMenu("&File", self)
        # filemenu.addAction("Load",self.onLoad)
        filemenu.addAction("Exit",self.onExit)
        loginmenu = QMenu("&Login", self)
        # loginmenu.addAction("Login", self.onLogin)
        # loginmenu.addAction("Create Account", self.onCreateAccount)
        menuBar.addMenu(filemenu)
        menuBar.addMenu(loginmenu)

        self.mainWidget = MainWidget(self)
        self.setCentralWidget(self.mainWidget)

        self.show()

    def onExit(self):
        dialog = YesOrNoDialog()
        if dialog.exec():
            exit(0)
        else:
            pass

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
        self.button.clicked.connect(self.login)
        self.show()

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

        self.playersframe = downloader.AutoDownloader.getPlayersFrame()
        self.teamsframe = downloader.AutoDownloader.getTeamsFrame()

        self.myTeam.layout.addWidget(UserTeamWidget(self, playersframe))

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

class UserTeamWidget(QWidget):
    def __init__(self, parent, playersframe):
        super(QWidget, self).__init__(parent)
        self.layout = QGridLayout(self)
        self.playersframe = playersframe

        self.tempframe = self.playersframe
        self.firstnames = self.playersframe["first_name"].to_list()
        self.secondnames = self.playersframe["second_name"].to_list()
        self.prices = self.playersframe["now_cost"].to_list()
        self.ids = self.playersframe["id"].to_list()
        self.fullnames = []
        for i in range(len(self.firstnames)):
            self.fullnames.append(self.firstnames[i] + " " + self.secondnames[i])
        self.namesandprices = []
        for i in range(len(self.fullnames)):
            currentdict = {"name": self.fullnames[i], "price": self.prices[i]}
            self.namesandprices.append(currentdict)

        file = open("data\\Evan-Team.json", "rb")
        data = file.read()
        self.teamdict = json.loads(data)
        file.close()

        self.sortSelector = QComboBox()
        items = ["Alphabetical", "Total Points", "Points Per Game"]
        self.sortSelector.addItems(items)
        self.sortSelector.currentIndexChanged.connect(self.setOrder)

        #creates dropdown
        self.attacker1 = QComboBox()
        self.attacker2 = QComboBox()
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
        self.layout.addWidget(self.attacker1,0,1)
        self.layout.addWidget(self.attacker2,0,3)
        self.layout.addWidget(self.midfielder1,1,1)
        self.layout.addWidget(self.midfielder2,1,2)
        self.layout.addWidget(self.midfielder3,1,3)
        self.layout.addWidget(self.defender1,2,0)
        self.layout.addWidget(self.defender2,2,1)
        self.layout.addWidget(self.defender3,2,2)
        self.layout.addWidget(self.defender4,2,3)
        self.layout.addWidget(self.defender5,2,4)
        self.layout.addWidget(self.goalkeeper,3,2)

        #resets to default layout
        self.resetButton = QPushButton("Reset")
        self.resetButton.clicked.connect(self.reset)

        self.createDropDowns(False, None)

        self.layout.addWidget(self.sortSelector)
        self.layout.addWidget(self.resetButton)

    def setOrder(self, type):
        if type == 0:
            dataframe = self.tempframe.sort_values("second_name")
        elif type == 1:
            dataframe = self.tempframe.sort_values("total_points")
        elif type == 2:
            dataframe = self.tempframe.sort_values("points_per_game")
        self.dataframe = dataframe
        self.createDropDowns(False, None)

    def createDropDowns(self, isPlayerTeam, idlist):
        positions = [1, 2, 2, 2, 2, 2, 3, 3, 3, 4, 4]
        if isPlayerTeam == False:
            self.goalkeepers = self.createPlayerLists(1, isPlayerTeam, None)
            self.defenders = self.createPlayerLists(2, isPlayerTeam, None)
            self.midfielders = self.createPlayerLists(3, isPlayerTeam, None)
            self.attackers = self.createPlayerLists(4, isPlayerTeam, None)
        for i in range(11):
            if isPlayerTeam == True:
                currentid = idlist[i]
                position = positions[i]
                if position == 1:
                    self.goalkeepers = self.createPlayerLists(1, isPlayerTeam, currentid)
                elif position == 2:
                    self.defenders = self.createPlayerLists(2, isPlayerTeam, currentid)
                elif position == 3:
                    self.midfielders = self.createPlayerLists(3, isPlayerTeam, currentid)
                elif position == 4:
                    self.attackers = self.createPlayerLists(4, isPlayerTeam, currentid)
            self.populateDropDown(i)
    
    def populateDropDown(self, num):
        positions = [self.goalkeeper, 
            self.defender1, 
            self.defender2, 
            self.defender3, 
            self.defender4, 
            self.defender5, 
            self.midfielder1, 
            self.midfielder2, 
            self.midfielder3, 
            self.attacker1, 
            self.attacker2]
        types = [self.goalkeepers, 
            self.defenders, 
            self.defenders, 
            self.defenders, 
            self.defenders, 
            self.defenders, 
            self.midfielders, 
            self.midfielders, 
            self.midfielders, 
            self.attackers, 
            self.attackers]
        currentposition = positions[num]
        currenttype = types[num]
        currentposition.clear()
        currentposition.addItems(currenttype)

    def createPlayerLists(self, typenum, isplayerteam, currentid):
        if isplayerteam == True:
            currentplayer = self.tempframe[self.tempframe["id"]==currentid]#gets player from the main dataframe
            currentfirstname = currentplayer.iloc[0, 12]#gets first name
            currentsecondname = currentplayer.iloc[0, 21]#gets first name
            currentname = currentfirstname + " " + currentsecondname
        playersframe = self.tempframe[self.tempframe["element_type"]==typenum]#gets all players in a position
        playersfirstname = playersframe["first_name"].to_list()
        playerssecondname = playersframe["second_name"].to_list()
        players = []
        for i in range(len(playersfirstname)):
            players.append(playersfirstname[i] + " " + playerssecondname[i])#adds first and last names together
        if isplayerteam == True:
            playerpos = players.index(currentname)#finds player position in list
            players.pop(playerpos)#removes player from list
            players.insert(0, currentname)#adds player to first position
        return players
    
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
            self.tempframe = self.playersframe
            for x in range(len(self.tempframe)):
                if self.tempframe.iloc[x,18] > remainingmoney:
                    self.tempframe.drop(self.tempframe.index[x])

    def setPlayerTeam(self):
        self.tempframe = self.tempframe.sort_values("second_name")
        idslist = list(self.teamdict.values())
        self.createDropDowns(True, idslist)

    def reset(self):
        self.setPlayerTeam()


def onStart():
    r = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    newdata = json.loads(r.content)
    file = open("data\\bootstrap-static.json", "rb")
    data = file.read()
    data = json.loads(data)
    if data != newdata:
        gameweeks = pd.DataFrame(newdata["events"])
        currentgameweek = getCurrentGameweek(gameweeks)
        downloader.AutoDownloader.downloadGenericData(currentgameweek)

def getCurrentGameweek(gameweeks):
    for i in range(len(gameweeks.index)):
        if gameweeks.iloc[i, 4] == "true":
            return i+1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App() 
    sys.exit(app.exec_())