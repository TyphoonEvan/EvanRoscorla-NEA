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
            self.icons[21] = QIcon("premiership_kits\\injured.png")
        return self.icons[teamID]

class UserTeamWidget(QWidget):
    def __init__(self, parent, playersframe):
        super(QWidget, self).__init__(parent)
        self.teamLayout = QVBoxLayout()
        self.pitchLayout = QGridLayout()
        self.buttonsFrame = QFrame()
        self.buttonsLayout = QVBoxLayout()
        self.mainlayout = QHBoxLayout()
        self.subsLayout = QHBoxLayout()
        self.playersframe = playersframe

        self.pitchLayout.setHorizontalSpacing(20)
        self.pitchLayout.setVerticalSpacing(60)
        self.buttonsFrame.setFixedWidth(200)

        self.buttonsFrame.setLayout(self.buttonsLayout)
        self.buttonsFrame.setFrameShape(1)
        self.teamLayout.addLayout(self.pitchLayout)
        self.teamLayout.addLayout(self.subsLayout)
        self.mainlayout.addLayout(self.teamLayout)
        self.mainlayout.addWidget(self.buttonsFrame)
        self.setLayout(self.mainlayout)

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
        self.fullnamesSeries = pd.Series(self.fullnames)
        
        self.injured = self.tempframe["chance_of_playing_this_round"].to_list()
        self.injured = pd.Series(self.injured)
        self.injured = pd.concat([self.injured, self.fullnamesSeries], axis=1)
        self.injured = self.injured.rename({0: "chance"}, axis=1)
        self.injured = self.injured.query("chance < 75")
        self.injured = self.injured.rename({"chance": "Chance to Play", 1: "Player"}, axis=1)
        self.injured = self.injured["Player"].to_list()

        self.sortSelector = QComboBox()
        items = ["Total Points", "Points Per Game", "Goals", "Assists", "Predicted Goals", "Predicted Assists", "Predicted Saves", "Predicted Points"]
        self.sortSelector.addItems(items)
        self.sortSelector.currentIndexChanged.connect(self.setOrder)
        
        self.droplist = []

        #creates dropdown
        self.player10 = QComboBox()
        self.player11 = QComboBox()
        self.player7 = QComboBox()
        self.player8 = QComboBox()
        self.player9 = QComboBox()
        self.player2 = QComboBox()
        self.player3 = QComboBox()
        self.player4 = QComboBox()
        self.player5 = QComboBox()
        self.player6 = QComboBox()
        self.player1 = QComboBox()

        self.sub4 = QComboBox()
        self.sub3 = QComboBox()
        self.sub2 = QComboBox()
        self.sub1 = QComboBox()

        self.player10.setFixedSize(150, 40)
        self.player11.setFixedSize(150, 40)
        self.player7.setFixedSize(150, 40)
        self.player8.setFixedSize(150, 40)
        self.player9.setFixedSize(150, 40)
        self.player2.setFixedSize(150, 40)
        self.player3.setFixedSize(150, 40)
        self.player4.setFixedSize(150, 40)
        self.player5.setFixedSize(150, 40)
        self.player6.setFixedSize(150, 40)
        self.player1.setFixedSize(150, 40)

        self.sub4.setFixedSize(150, 40)
        self.sub3.setFixedSize(150, 40)
        self.sub2.setFixedSize(150, 40)
        self.sub1.setFixedSize(150, 40)

        self.player10.setIconSize(QSize(40, 32))
        self.player11.setIconSize(QSize(40, 32))
        self.player7.setIconSize(QSize(40, 32))
        self.player8.setIconSize(QSize(40, 32))
        self.player9.setIconSize(QSize(40, 32))
        self.player2.setIconSize(QSize(40, 32))
        self.player3.setIconSize(QSize(40, 32))
        self.player4.setIconSize(QSize(40, 32))
        self.player5.setIconSize(QSize(40, 32))
        self.player6.setIconSize(QSize(40, 32))
        self.player1.setIconSize(QSize(40, 32))
        
        self.sub4.setIconSize(QSize(40, 32))
        self.sub3.setIconSize(QSize(40, 32))
        self.sub2.setIconSize(QSize(40, 32))
        self.sub1.setIconSize(QSize(40, 32))

        #resets to default layout
        self.resetButton = QPushButton("Reset")
        self.resetButton.clicked.connect(self.reset)

        self.saveButton = QPushButton("Save Team")
        self.saveButton.clicked.connect(self.saveTeam)

        self.dataframe = self.tempframe.sort_values("second_name")
        self.createDropDowns(False, None, None)
        self.setUserTeam(1)
        self.setFormation()

        self.sortSelector.setFixedSize(150, 40)
        self.resetButton.setFixedSize(150, 40)
        self.saveButton.setFixedSize(150, 40)

        self.buttonsLayout.addWidget(self.sortSelector)
        self.buttonsLayout.addWidget(self.resetButton)
        self.buttonsLayout.addWidget(self.saveButton)

        self.subsLayout.addWidget(self.sub1)
        self.subsLayout.addWidget(self.sub2)
        self.subsLayout.addWidget(self.sub3)
        self.subsLayout.addWidget(self.sub4)

    def getUserTeam(self):
        filename = self.GetLastModified("teams").name
        filename = "teams\\"+filename
        with open(filename, "rb") as file:
            data = file.read()
            data = json.loads(data)
            file.close()
            return data
        
    def sortDataframes(self, type):
        items = ["total_points", "points_per_game", "goals_scored", "assists", "predicted_goals_scored", "predicted_assists", "predicted_saves", "predicted_points_per_game"]
        type = items[type]

        self.goalkeepersframe = self.tempframe.query("element_type == 1")
        self.defendersframe = self.tempframe.query("element_type == 2")
        self.midfieldersframe = self.tempframe.query("element_type == 3")
        self.attackersframe = self.tempframe.query("element_type == 4")

        self.goalkeepersframe.sort_values(type, ascending=False)
        self.defendersframe.sort_values(type, ascending=False)
        self.midfieldersframe.sort_values(type, ascending=False)
        self.attackersframe.sort_values(type, ascending=False)

        self.goalkeepers = []
        for i in range(len(self.goalkeepersframe.index)):
            currentid = self.goalkeepersframe["id"].iloc[i]
            index = self.ids.index(currentid)
            name = self.fullnames[index]
            self.goalkeepers.append(name)

        self.defenders = []
        for i in range(len(self.defendersframe.index)):
            currentid = self.defendersframe["id"].iloc[i]
            index = self.ids.index(currentid)
            name = self.fullnames[index]
            self.defenders.append(name)

        self.midfielders = []
        for i in range(len(self.midfieldersframe.index)):
            currentid = self.midfieldersframe["id"].iloc[i]
            index = self.ids.index(currentid)
            name = self.fullnames[index]
            self.midfielders.append(name)

        self.attackers = []
        for i in range(len(self.attackersframe.index)):
            currentid = self.attackersframe["id"].iloc[i]
            index = self.ids.index(currentid)
            name = self.fullnames[index]
            self.attackers.append(name)

    def setOrder(self, type):
        team, subs = self.sortTeam(type)
        team = team.sort_values("element_type")
        team = pd.concat([team, subs], axis=0)
        data = self.getUserTeam()
        ids = team["id"].to_list()
        for i in range(len(ids)):
            id = ids[i]
            data[str(i+1)] = id
        data = json.dumps(data)
        filename = self.GetLastModified("teams").name
        filename = "teams\\"+filename
        with open(filename, "w") as file:
            file.write(data)
            file.close()
        self.setUserTeam(type)

    def sortTeam(self, type):
        dropdowns = [self.player2, 
            self.player3, 
            self.player4, 
            self.player5, 
            self.player6, 
            self.player7, 
            self.player8, 
            self.player9, 
            self.player10, 
            self.player11,
            self.sub1,
            self.sub2,
            self.sub3,
            self.sub4]
        currentplayer = str(self.player1.currentText())
        namePosition = self.fullnames.index(currentplayer)
        currentID = self.ids[namePosition]
        player = self.tempframe.query("id == @currentID")
        teamframe = player
        for i in range(len(dropdowns)):
            currentdropdown = dropdowns[i]
            currentplayer = str(currentdropdown.currentText())
            namePosition = self.fullnames.index(currentplayer)
            currentID = self.ids[namePosition]
            player = self.tempframe.query("id == @currentID")
            teamframe = pd.concat([teamframe, player], axis=0)
        items = ["total_points", "points_per_game", "goals_scored", "assists", "predicted_goals_scored", "predicted_assists", "predicted_saves", "predicted_points_per_game"]
        teamframe = teamframe.sort_values(items[type], ascending=False)
        try:
            teamframe = teamframe.reset_index()
        except ValueError:
            pass
        valid = False
        while valid == False:
            team = teamframe.head(11)
            subs = teamframe.tail(4)
            positions = team["element_type"].to_list()
            if positions.count(1) != 0:
                if positions.count(2) >= 1 and positions.count(2) <= 5:
                    if positions.count(3) >= 1 or positions.count(3) <= 5:
                        if positions.count(4) >= 1 or positions.count(4) <= 5:
                            valid = True
                            team = teamframe.head(11)
                            subs = teamframe.tail(4)
                            return team, subs
                        else:
                            temp = teamframe.head(1)
                            teamframe.drop(1, axis=0)
                            teamframe = pd.concat([teamframe, temp], axis=0)
                    else:
                        temp = teamframe.head(1)
                        teamframe.drop(1, axis=0)
                        teamframe = pd.concat([teamframe, temp], axis=0)
                else:
                    temp = teamframe.head(1)
                    teamframe.drop(1, axis=0)
                    teamframe = pd.concat([teamframe, temp], axis=0)
            else:
                temp = teamframe.head(1)
                teamframe.drop(1, axis=0)
                teamframe = pd.concat([teamframe, temp], axis=0)
                    
    def createDropDowns(self, isPlayerTeam, idlist, type):
        if isPlayerTeam == False:
            self.goalkeepers = self.createPlayerLists(1, isPlayerTeam, None, 1)
            self.defenders = self.createPlayerLists(2, isPlayerTeam, None, 1)
            self.midfielders = self.createPlayerLists(3, isPlayerTeam, None, 1)
            self.attackers = self.createPlayerLists(4, isPlayerTeam, None, 1)
        for i in range(11):
            if isPlayerTeam == True:
                currentid = idlist[i]
                position = self.getPosition(currentid)
                if position == 1:
                    self.goalkeepers = self.createPlayerLists(1, isPlayerTeam, currentid, type)
                elif position == 2:
                    self.defenders = self.createPlayerLists(2, isPlayerTeam, currentid, type)
                elif position == 3:
                    self.midfielders = self.createPlayerLists(3, isPlayerTeam, currentid, type)
                elif position == 4:
                    self.attackers = self.createPlayerLists(4, isPlayerTeam, currentid, type)
            self.populateDropDown(i)
    
    def populateDropDown(self, num):
        positions = [self.player1, 
            self.player2, 
            self.player3, 
            self.player4, 
            self.player5, 
            self.player6, 
            self.player7, 
            self.player8, 
            self.player9, 
            self.player10, 
            self.player11]
        types = [self.goalkeepers, 
            self.defenders, 
            self.defenders, 
            self.defenders, 
            self.defenders, 
            self.midfielders, 
            self.midfielders, 
            self.midfielders, 
            self.midfielders, 
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

    def createPlayerLists(self, typenum, isplayerteam, currentid, type):
        currentname = ""
        if isplayerteam == True:
            currentplayer = self.playersframe[self.playersframe["id"]==currentid]#gets player from the main dataframe
            currentfirstname = currentplayer["first_name"].to_list()[0]#gets first name
            currentsecondname = currentplayer["second_name"].to_list()[0]#gets first name
            currentname = currentfirstname + " " + currentsecondname
            self.priceUpdate()
        players = self.createNamesList(typenum, isplayerteam, self.tempframe, currentname, type)
        return players
    
    def createNamesList(self, typenum, isplayerteam, playersframe, currentname, type):
        playersframe = playersframe[playersframe["element_type"]==typenum]#gets all players in a position
        items = ["total_points", "points_per_game", "goals_scored", "assists", "predicted_goals_scored", "predicted_assists", "predicted_saves", "predicted_points_per_game"]
        type = items[type]
        playersframe = playersframe.sort_values(type, ascending=False)
        if isplayerteam == True:
            playersframe = self.removeExpensive(playersframe, currentname, typenum)
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
    
    def removeExpensive(self, playersframe, currentname, typenum):
        index = self.fullnames.index(currentname)
        price = self.namesandprices[index]["price"]
        expensivelist = []
        for i in range(len(self.droplist)):
            index = self.droplist[i]
            id = self.ids[index]
            player = self.playersframe[self.playersframe["id"]==id]
            if player["element_type"].to_list()[0] == typenum:
                currentprice = self.prices[index]
                if currentprice > price:
                    expensivelist.append(index)
        playersframe = playersframe.drop(index=expensivelist, axis=0)
        return playersframe
    
    def priceUpdate(self):
        maxprice = 1000
        totalcost = 0
        dropdownslist = [self.player1, self.player2, self.player3, self.player4, self.player5, self.player6, self.player7, self.player8, self.player9, self.player10, self.player11, self.sub1, self.sub2, self.sub3, self.sub4]
        for i in range(15):
            currentdropdown = dropdownslist[i]
            currentplayer = str(currentdropdown.currentText())
            for i in range(len(self.namesandprices)):
                if currentplayer == self.namesandprices[i]["name"]:
                    cost = self.namesandprices[i]["price"]
                    break
            totalcost+=cost
        remainingmoney = maxprice-totalcost
        try:
            self.playersframe = self.playersframe.reset_index()
        except ValueError:
            pass
        self.tempframe = self.playersframe
        self.droplist = []
        for x in range(len(self.tempframe.index)):
            if self.tempframe["now_cost"].iloc[x] > remainingmoney:
                self.droplist.append(x)

    def setUserTeam(self, type):
        self.tempframe = self.tempframe.sort_values("second_name")
        self.teamdict = self.getUserTeam()
        idslist = list(self.teamdict.values())
        teamlist = idslist[:11]
        subslist = idslist[11:]
        self.createDropDowns(True, teamlist, type)
        self.populateSubs(True, subslist)

    def saveTeam(self):
        dropdownslist = [self.player1, self.player2, self.player3, self.player4, self.player5, self.player6, self.player7, self.player8, self.player9, self.player10, self.player11, self.sub1, self.sub2, self.sub3, self.sub4]
        data = self.getUserTeam()
        for i in range(11):
            currentdropdown = dropdownslist[i]
            currentplayer = str(currentdropdown.currentText())
            index = self.fullnames.index(currentplayer)
            id = self.ids[index]
            data[str(i+1)] = id
        data = json.dumps(data)
        filename = self.GetLastModified("teams").name
        filename = "teams\\"+filename
        with open(filename, "w") as file:
            file.write(data)
            file.close()

    def reset(self):
        self.setUserTeam(1)

    def getPosition(self, id):
        player = self.tempframe.query("id == @id")
        position = player.loc[:, "element_type"].to_list()[0]
        return position
    
    def setFormation(self):
        positions = {1:[2], 2:[1,3], 3:[0,2,4], 4:[0,1,3,4], 5:[0,1,2,3,4,5]}
        positionsList = []
        team = self.getUserTeam()
        for i in range(11):
            id = team[str(i+1)]
            position = self.getPosition(id)
            positionsList.append(position)
        forwards = positions[positionsList.count(4)]
        midfielders = positions[positionsList.count(3)]
        defenders = positions[positionsList.count(2)]
        positionsList = []
        positionsList = defenders + midfielders + forwards
        playersList = [self.player2, self.player3, self.player4, self.player5, self.player6, self.player7, self.player8, self.player9, self.player10, self.player11]
        self.pitchLayout.addWidget(self.player1,4,2)
        for i in range(10):
            if (i) < len(defenders):
                self.pitchLayout.addWidget(playersList[i],3,positionsList[i])
            elif (i) < (len(defenders)+len(midfielders)):
                self.pitchLayout.addWidget(playersList[i],2,positionsList[i])
            elif (i) < (len(defenders)+len(midfielders)+len(forwards)):
                self.pitchLayout.addWidget(playersList[i],1,positionsList[i])

    def populateSubs(self, isPlayerTeam, idslist):
        if isPlayerTeam == True:
            positions = []
            for i in range(4):
                positions.append(self.getPosition(idslist[i]))
        else:
            positions = [self.goalkeepers, self.defenders, self.midfielders, self.attackers]
        dropdowns = [self.sub1, self.sub2, self.sub3, self.sub4]
        for i in range(4):
            if isPlayerTeam == True:
                positions[i] = self.createPlayerLists(positions[i], True, idslist[i], 1)
            dropdowns[i].clear()
            for player in positions[i]:
                namePosition = self.fullnames.index(player)
                currentID = self.ids[namePosition]
                df = self.tempframe.query("id == @currentID")
                if player in self.injured:
                    team = 21
                else:
                    team = df["team"].to_list()[0]
                icon = IconGenerator.GetIcon(team)
                dropdowns[i].addItem(icon, player)

    @staticmethod
    def GetLastModified(dir):
        items = os.scandir(dir)
        def get_modified(entry):
            return entry.stat().st_mtime
        sorted = []
        for item in items:
            sorted.append(item)
        sorted.sort(key=get_modified, reverse=False)     
        return sorted.pop()   