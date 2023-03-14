from lib2to3.pgen2 import driver
import sys, os, configparser
import json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt 
from download import downloader
import pandas as pd
from team_optimiser import *
from cryptography.fernet import Fernet
import ast
import requests
from summary_page import SummaryPage
from player_table import PlayerTable
from user_team import UserTeamWidget
from graphs import GraphPage
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
        self.setWindowIcon(QIcon("Icon.png"))

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
        self.setWindowTitle("Create Account")

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
        self.setWindowTitle("Login")
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
    UserTeamWidget.getUserTeam(UserTeamWidget)

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
        self.graphTab = QWidget()
        self.summaryPage = SummaryPage(self)
        self.graphs = GraphPage(self)
        self.tabs.resize(300,200)

        self.tabs.addTab(self.summaryPage,"Summary")
        self.tabs.addTab(self.myTeam,"My Team")
        self.tabs.addTab(self.playerStats,"Player Stats")
        self.tabs.addTab(self.graphTab,"Graphs")

        self.tabs.currentChanged.connect(self.onReload)

        self.myTeam.layout = QVBoxLayout(self.myTeam)
        self.playerStats.layout = QVBoxLayout(self.playerStats)
        self.graphTab.layout = QVBoxLayout(self.graphTab)

        self.playerStats.layout.addWidget(PlayerTable(self))
        self.getData()

        self.userTeamWidget = UserTeamWidget(self, self.playersframe)

        self.myTeam.layout.addWidget(self.userTeamWidget)

        self.graphTab.layout.addWidget(self.graphs)

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
        if self.reload is True:
            self.getData()
            self.reload = False

async def onStart(app):
    '''Checks if the downloaded data is out of date, if so it downloads new data'''
    r = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    newdata = json.loads(r.content)
    with open("data\\bootstrap-static.json", "rb") as file:
        data = file.read()
        file.close()
    data = json.loads(data)
    if data != newdata:
        gameweeks = pd.DataFrame(newdata["events"])
        currentgameweek = getCurrentGameweek(gameweeks)
        downloader.AutoDownloader.downloadGenericData(currentgameweek)
    widget = ex.centralWidget()
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