from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot, Qt, QAbstractTableModel
import pandas as pd
import json
import requests
import sys

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

        self.setCentralWidget(SummaryPage(self))
        self.show()

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

class SummaryPage(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.mainlayout = QVBoxLayout()
        self.toplayout = QHBoxLayout()
        self.bottomlayout = QHBoxLayout()
        self.performanceLayout = QHBoxLayout()
        self.buttonslayout = QVBoxLayout()
        self.userteamlayout = QGridLayout()

        self.fixturesLayout = QVBoxLayout()
        self.allTimePerformanceLayout = QVBoxLayout()
        self.valueForMoneyLayout = QVBoxLayout()
        self.gameweekPerformanceLayout = QVBoxLayout()
        self.injuredLayout = QVBoxLayout()

        self.fixturesBox = QGroupBox("Fixtures")
        self.fixturesBox.setLayout(self.fixturesLayout)

        self.allTimePerformanceBox = QGroupBox("Overall Performance")
        self.allTimePerformanceBox.setLayout(self.allTimePerformanceLayout)

        self.valueForMoneyBox = QGroupBox("Value for Money")
        self.valueForMoneyBox.setLayout(self.valueForMoneyLayout)

        self.gameweekPerformanceBox = QGroupBox("Current Performance")
        self.gameweekPerformanceBox.setLayout(self.gameweekPerformanceLayout)

        self.injuredBox = QGroupBox("Injuries")
        self.injuredBox.setLayout(self.injuredLayout)

        file = open("data.json", "rb")
        data = file.read()
        data = json.loads(data)
        playersframe = pd.DataFrame(data)
        playersframe = playersframe[["id", "first_name", "second_name", "team",
       "total_points", "goals_scored", "assists", "minutes", "points_per_game",
       "saves", "clean_sheets", "ict_index", "influence", "creativity",
       "threat", "now_cost", "element_type", "chance_of_playing_this_round",
       "predicted_goals_scored", "predicted_assists", "predicted_saves",
       "predicted_clean_sheets", "predicted_points_per_game",
       "average_play_time"]]
        self.playersframe = playersframe.sort_values("id")
        self.tempplayersframe = self.playersframe

        self.toplayout.addLayout(self.performanceLayout)
        self.bottomlayout.addLayout(self.buttonslayout)
        self.mainlayout.addLayout(self.toplayout)
        self.mainlayout.addLayout(self.bottomlayout)

        self.createWidgets()

    def createWidgets(self):
        self.firstnames = self.tempplayersframe["first_name"].to_list()
        self.secondnames = self.tempplayersframe["second_name"].to_list()
        self.fullnames = []
        for i in range(len(self.firstnames)):
            self.fullnames.append(self.firstnames[i] + " " + self.secondnames[i])
        self.fullnames = pd.Series(self.fullnames)

        self.injured = self.tempplayersframe["chance_of_playing_this_round"].to_list()
        self.injured = pd.Series(self.injured)
        self.injured = pd.concat([self.injured, self.fullnames], axis=1)
        self.injured = self.injured.rename({0: "chance"}, axis=1)
        self.injured = self.injured.query("chance < 100")
        self.injured = self.injured.rename({"chance": "Chance to Play", 1: "Player"}, axis=1)

        r = requests.get("https://fantasy.premierleague.com/api/fixtures")
        data = json.loads(r.content)
        dataframe = pd.DataFrame(data)
        dataframe = dataframe[dataframe["finished"]==True]
        self.fixtures = dataframe[["team_h", "team_a", "event"]]

        r = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
        data = json.loads(r.content)
        gameweeks = pd.DataFrame(data["events"])
        currentgameweek = float(getCurrentGameweek(gameweeks))

        file = open("data\\Evan-Team.json", "rb")
        data = file.read()
        file.close()
        teamdict = json.loads(data)

        self.fixtures = self.fixtures.query("event == @currentgameweek")

        self.fixtures = self.fixtures.rename({"team_h": "Home Team", "team_a": "Away Team"}, axis=1).drop("event", axis=1)

        self.points = self.tempplayersframe["total_points"].to_list()
        self.predictedPoints = self.tempplayersframe["predicted_points_per_game"].to_list()
        self.playerCosts = self.tempplayersframe["now_cost"].to_list()

        for i in range(len(self.points)):
            predicted = self.predictedPoints[i]
            points = self.points[i]
            self.predictedPoints[i] = round(predicted - points)

        self.valueForMoneyList = []
        for i in range(len(self.points)):
            self.valueForMoneyList.append(self.points[i]/self.playerCosts[i])

        for i in range(len(self.valueForMoneyList)):
            self.valueForMoneyList[i] = round(self.valueForMoneyList[i], 1)

        self.points = pd.Series(self.points)
        self.predictedPoints = pd.Series(self.predictedPoints)
        self.valueForMoneyList = pd.Series(self.valueForMoneyList)

        self.points = pd.concat([self.fullnames, self.points], axis=1)
        self.predictedPoints = pd.concat([self.fullnames, self.predictedPoints], axis=1)
        self.valueForMoneyList = pd.concat([self.fullnames, self.valueForMoneyList], axis=1)

        self.points = self.points.rename({0: "Player", 1: "Points"}, axis=1)
        self.predictedPoints = self.predictedPoints.rename({0: "Player", 1: "Points"}, axis=1)
        self.valueForMoneyList = self.valueForMoneyList.rename({0: "Player", 1: "V/M"}, axis=1)

        self.points = self.points.sort_values("Points", ascending=False)
        self.predictedPoints = self.predictedPoints.sort_values("Points", ascending=False)
        self.valueForMoneyList = self.valueForMoneyList.sort_values("V/M", ascending=False)

        self.points = self.points.head(10)
        self.predictedPoints = self.predictedPoints.head(10)
        self.valueForMoneyList = self.valueForMoneyList.head(10)

        self.fixturesTable = QTableView()
        fixturesModel = pandasModel(self.fixtures)
        self.fixturesTable.setModel(fixturesModel)

        self.allTimePerformanceTable = QTableView()
        allTimePerformanceModel = pandasModel(self.points)
        self.allTimePerformanceTable.setModel(allTimePerformanceModel)

        self.valueForMoneyTable = QTableView()
        valueForMoneyModel = pandasModel(self.valueForMoneyList)
        self.valueForMoneyTable.setModel(valueForMoneyModel)

        self.gameweekPerformanceTable = QTableView()
        gameweekPerformanceModel = pandasModel(self.predictedPoints)
        self.gameweekPerformanceTable.setModel(gameweekPerformanceModel)

        self.injuredTable = QTableView()
        injuredModel = pandasModel(self.injured)
        self.injuredTable.setModel(injuredModel)

        self.positionSelector = QComboBox()
        self.positionSelector.addItems(["All", "Goalkeepers", "Defenders", "Midfielders", "Attackers"])
        self.positionSelector.currentIndexChanged.connect(self.changePosition)

        self.fixturesLayout.addWidget(self.fixturesTable)
        self.allTimePerformanceLayout.addWidget(self.allTimePerformanceTable)
        self.valueForMoneyLayout.addWidget(self.valueForMoneyTable)
        self.gameweekPerformanceLayout.addWidget(self.gameweekPerformanceTable)
        self.injuredLayout.addWidget(self.injuredTable)

        self.bottomlayout.addWidget(self.positionSelector)
        self.bottomlayout.addWidget(self.fixturesBox)
        self.performanceLayout.addWidget(self.allTimePerformanceBox)
        self.performanceLayout.addWidget(self.valueForMoneyBox)
        self.performanceLayout.addWidget(self.gameweekPerformanceBox)
        self.bottomlayout.addWidget(self.injuredBox)

        self.setLayout(self.mainlayout)
    
    def changePosition(self, position):
        if position != 0:
            self.tempplayersframe = self.playersframe[self.playersframe["element_type"] == position]
        else:
            self.tempplayersframe = self.playersframe
        self.bottomlayout.removeWidget(self.positionSelector)
        self.bottomlayout.removeWidget(self.fixturesTable)
        self.performanceLayout.removeWidget(self.allTimePerformanceTable)
        self.performanceLayout.removeWidget(self.valueForMoneyTable)
        self.performanceLayout.removeWidget(self.gameweekPerformanceTable)
        self.bottomlayout.removeWidget(self.injuredTable)
        self.createWidgets()

def getCurrentGameweek(gameweeks):
    for i in range(len(gameweeks.index)):
        if gameweeks.iloc[i, 4] == False:
            return i+1


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App() 
    sys.exit(app.exec_())