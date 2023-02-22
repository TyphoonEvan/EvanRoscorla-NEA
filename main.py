from lib2to3.pgen2 import driver
import sys, os, configparser
import json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot, Qt, QAbstractTableModel, QSize
from download import downloader
import pandas as pd
from team_optimiser import *
from cryptography.fernet import Fernet
import ast
import requests
from summary_page import SummaryPage
from player_table import PlayerTable
import asyncio

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

        splash_pix = QPixmap("splash_screen.png")
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.show()

        self.mainWidget = MainWidget(self)
        self.setCentralWidget(self.mainWidget)
        file = open("stylesheet.txt", "r")
        stylesheet = file.read()
        self.setStyleSheet(stylesheet)

        menuBar = QMenuBar(self)
        self.setMenuBar(menuBar)
        filemenu = QMenu("&File", self)
        filemenu.addAction("Exit",self.onExit)
        loginmenu = QMenu("&Accounts", self)
        loginmenu.addAction("Login", self.onLogin)
        loginmenu.addAction("Create Account", self.onCreateAccount)
        menuBar.addMenu(filemenu)
        menuBar.addMenu(loginmenu)

        splash.close()
        self.show()

    def onExit(self):
        dialog = YesOrNoDialog()
        if dialog.exec():
            exit(0)
        else:
            pass

    def onCreateAccount(self):
        self.accountCreatorDialog = CreateAccount()

    def onLogin(self):
        self.loginDialog = Login()

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

    def login(self):
        username = self.nameline.text()
        password = self.passwordline.text()

        filename = "config\\" + username + ".cnfg"
        file = open(filename, "rb")
        data = file.read()
        file.close()

        keyFile = open("key.key", "rb")
        key = keyFile.read()
        file.close()
        f = Fernet(key)
        data = f.decrypt(data)
        data = data.decode("utf-8")
        data = ast.literal_eval(data)
        if data["password"] == password:
            globalGetUserTeam(username)           

def globalGetUserTeam(username):
    UserTeamWidget.getUserTeam(UserTeamWidget, username)

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

        self.reload = False

        self.tabs = QTabWidget()
        self.myTeam = QWidget()
        self.playerStats = QWidget()
        self.teamStats = QWidget()
        self.summaryPage = SummaryPage(self)
        self.tabs.resize(300,200)

        self.tabs.addTab(self.myTeam,"My Team")
        self.tabs.addTab(self.playerStats,"Player Stats")
        self.tabs.addTab(self.teamStats,"Team Stats")
        self.tabs.addTab(self.summaryPage,"Summary")

        self.tabs.currentChanged.connect(self.onReload)

        self.myTeam.layout = QVBoxLayout(self.myTeam)
        self.playerStats.layout = QVBoxLayout(self.playerStats)
        self.teamStats.layout = QVBoxLayout(self.teamStats)

        self.playerStats.layout.addWidget(PlayerTable(self))
        self.getData()

        self.userTeamWidget = UserTeamWidget(self, self.playersframe)

        self.myTeam.layout.addWidget(self.userTeamWidget)

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def getData(self):
        self.downloader = downloader.AutoDownloader()
        file = open("data\\player-data.json", "r")
        data = file.read()
        data = json.loads(data)
        self.playersframe = pd.DataFrame(data)
        self.teamsframe = self.downloader.getTeamsFrame()

    def onReload(self):
        if self.reload == True:
            self.getData()
            self.reload = False

class IconGenerator:

    icons = {}

    @classmethod
    def GetIcon(self, teamID):
        # Create dictionary of icons
        if not len(self.icons):
            self.icons[1] = QIcon("premiership_kits\\Arsenal_home.png")
            self.icons[2] = QIcon("premiership_kits\\Aston_Villa_home.png")
            self.icons[3] = QIcon("premiership_kits\\Bournemouth_home.png")
            self.icons[4] = QIcon("premiership_kits\\Brentford_home.png")
            self.icons[5] = QIcon("premiership_kits\\Brighton_home.png")
            self.icons[6] = QIcon("premiership_kits\\Chelsea_home.png")
            self.icons[7] = QIcon("premiership_kits\\Crystal_Palace_home.png")
            self.icons[8] = QIcon("premiership_kits\\Everton_home.png")
            self.icons[9] = QIcon("premiership_kits\\Fulham_home.png")
            self.icons[10] = QIcon("premiership_kits\\Leeds_home.png")
            self.icons[11] = QIcon("premiership_kits\\Leicester_home.png")
            self.icons[12] = QIcon("premiership_kits\\Liverpool_home.png")
            self.icons[13] = QIcon("premiership_kits\\Manchester_City_home.png")
            self.icons[14] = QIcon("premiership_kits\\Manchester_United_home.png")
            self.icons[15] = QIcon("premiership_kits\\Newcastle_home.png")
            self.icons[16] = QIcon("premiership_kits\\Nottingham_Forest_home.png")
            self.icons[17] = QIcon("premiership_kits\\Southampton_home.png")
            self.icons[18] = QIcon("premiership_kits\\Tottenham_Hotspur_home.png")
            self.icons[19] = QIcon("premiership_kits\\West_Ham_home.png")
            self.icons[20] = QIcon("premiership_kits\\Wolves_home.png")
        return self.icons[teamID]

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

        self.sortSelector = QComboBox()
        items = ["Alphabetical", "Total Points", "Points Per Game"]
        self.sortSelector.addItems(items)
        self.sortSelector.currentIndexChanged.connect(self.setOrder)

        #creates dropdown
        self.attacker2 = QComboBox()
        self.attacker3 = QComboBox()
        self.midfielder3 = QComboBox()
        self.midfielder4 = QComboBox()
        self.attacker1 = QComboBox()
        self.defender1 = QComboBox()
        self.defender2 = QComboBox()
        self.defender3 = QComboBox()
        self.midfielder1 = QComboBox()
        self.midfielder2 = QComboBox()
        self.goalkeeper = QComboBox()

        self.attacker2.setFixedSize(150, 40)
        self.attacker3.setFixedSize(150, 40)
        self.midfielder3.setFixedSize(150, 40)
        self.midfielder4.setFixedSize(150, 40)
        self.attacker1.setFixedSize(150, 40)
        self.defender1.setFixedSize(150, 40)
        self.defender2.setFixedSize(150, 40)
        self.defender3.setFixedSize(150, 40)
        self.midfielder1.setFixedSize(150, 40)
        self.midfielder2.setFixedSize(150, 40)
        self.goalkeeper.setFixedSize(150, 40)

        self.attacker2.setIconSize(QSize(40, 32))
        self.attacker3.setIconSize(QSize(40, 32))
        self.midfielder3.setIconSize(QSize(40, 32))
        self.midfielder4.setIconSize(QSize(40, 32))
        self.attacker1.setIconSize(QSize(40, 32))
        self.defender1.setIconSize(QSize(40, 32))
        self.defender2.setIconSize(QSize(40, 32))
        self.defender3.setIconSize(QSize(40, 32))
        self.midfielder1.setIconSize(QSize(40, 32))
        self.midfielder2.setIconSize(QSize(40, 32))
        self.goalkeeper.setIconSize(QSize(40, 32))
        #adds dropdowns to tab
        self.layout.addWidget(self.attacker2,0,0)
        self.layout.addWidget(self.attacker3,0,4)
        self.layout.addWidget(self.midfielder3,1,0)
        self.layout.addWidget(self.midfielder4,1,1)
        self.layout.addWidget(self.attacker1,0,2)
        self.layout.addWidget(self.defender1,2,1)
        self.layout.addWidget(self.defender2,2,2)
        self.layout.addWidget(self.defender3,2,3)
        self.layout.addWidget(self.midfielder1,1,3)
        self.layout.addWidget(self.midfielder2,1,4)
        self.layout.addWidget(self.goalkeeper,3,2)

        #resets to default layout
        self.resetButton = QPushButton("Reset")
        self.resetButton.clicked.connect(self.reset)

        self.createDropDowns(False, None)

        self.layout.addWidget(self.sortSelector)
        self.layout.addWidget(self.resetButton)

    def getUserTeam(self, username):
        userdownloader = downloader.AutoDownloader()
        teamdict = userdownloader.getUserData(username)

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
        positions = [1, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4]
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
            self.midfielder1, 
            self.midfielder2, 
            self.midfielder3, 
            self.midfielder4, 
            self.attacker1, 
            self.attacker2, 
            self.attacker3]
        types = [self.goalkeepers, 
            self.defenders, 
            self.defenders, 
            self.defenders, 
            self.midfielders, 
            self.midfielders, 
            self.midfielders, 
            self.midfielders, 
            self.attackers, 
            self.attackers, 
            self.attackers]
        currentposition = positions[num]
        currenttype = types[num]
        currentposition.clear()
        for player in currenttype:
            namePosition = self.fullnames.index(player)
            currentID = self.ids[namePosition]
            df = self.tempframe.query("id == @currentID")
            team = df["team"].to_list()[0]
            icon = IconGenerator.GetIcon(team)
            currentposition.addItem(icon, player)

    def createPlayerLists(self, typenum, isplayerteam, currentid):
        if isplayerteam == True:
            currentplayer = self.tempframe[self.tempframe["id"]==currentid]#gets player from the main dataframe
            currentfirstname = currentplayer.iloc[0, 2]#gets first name
            currentsecondname = currentplayer.iloc[0, 3]#gets first name
            currentname = currentfirstname + " " + currentsecondname
        players = self.createNamesList(typenum, isplayerteam, self.tempframe, currentname)
        return players
    
    @staticmethod
    def createNamesList(typenum, isplayerteam, playersframe, currentname):
        playersframe = playersframe[playersframe["element_type"]==typenum]#gets all players in a position
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
        dropdownslist = [self.goalkeeper, self.defender1, self.defender2, self.defender3, self.midfielder1, self.midfielder2, self.midfielder3, self.midfielder4, self.attacker1, self.forward1, self.forward2]
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
        file = open("data\\Evan-Team.json", "rb")
        data = file.read()
        file.close()
        self.teamdict = json.loads(data)
        idslist = list(self.teamdict.values())
        self.createDropDowns(True, idslist)

    def reset(self):
        self.setPlayerTeam()


async def onStart(app):
    '''Checks if the downloaded data is out of date, if so it downloads new data'''
    r = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    newdata = json.loads(r.content)
    file = open("data\\bootstrap-static.json", "rb")
    data = file.read()
    data = json.loads(data)
    if data != newdata:
        gameweeks = pd.DataFrame(newdata["events"])
        currentgameweek = getCurrentGameweek(gameweeks)
        downloader.AutoDownloader.downloadGenericData(currentgameweek)
    widget = ex.centralWidget()
    # hasattr just to be certain
    if hasattr(widget, 'reload'):
        widget.reload = True

def getCurrentGameweek(gameweeks):
    for i in range(len(gameweeks.index)):
        if gameweeks.iloc[i, 4] == "true":
            return i+1
        
async def runGUI(app):
    app.exec_()

async def runAll(app):
    await asyncio.gather(onStart(app), runGUI(app)) 

teamdict = ""
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(asyncio.run(runAll(app)))