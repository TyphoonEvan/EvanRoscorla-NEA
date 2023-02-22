from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, Qt, QAbstractTableModel
import json
import pandas as pd
import sys

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

class PlayerTable(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.mainlayout = QVBoxLayout(self)
        self.playerslayout = QTableView()
        self.searchLayout = QHBoxLayout(self)
        self.searchBar = QLineEdit(self)
        self.searchButton = QPushButton("Search")
        self.searchButton.clicked.connect(self.searchTable)
        self.searchLayout.addWidget(self.searchBar)
        self.searchLayout.addWidget(self.searchButton)
        self.getTableData()
        self.createPlayerTable()
        self.mainlayout.addLayout(self.searchLayout)
        self.mainlayout.addWidget(self.playerslayout)

    def getTableData(self):
        file = open("data.json", "rb")
        data = file.read()
        data = json.loads(data)
        self.dataframe = pd.DataFrame(data)
        self.dataframe = self.dataframe.drop(["index", "code", "team", "minutes", "ict_index", "influence", "creativity", "threat", "now_cost", "element_type", "id_avg", "average_play_time"], axis=1)
        self.firstnames = self.dataframe["first_name"].to_list()
        self.secondnames = self.dataframe["second_name"].to_list()
        self.fullnames = []
        for i in range(len(self.firstnames)):
            self.fullnames.append(self.firstnames[i] + " " + self.secondnames[i])
        self.dataframe = self.dataframe.drop(["second_name", "predicted_clean_sheets"], axis=1)
        self.dataframe = self.dataframe.replace(self.dataframe["first_name"].values, self.fullnames)
        self.dataframe = self.dataframe.rename({"id": "ID", "first_name": "Player name","total_points": "Total points", "goals_scored": "Goals", "assists": "Assists", "points_per_game": "Points per game", "saves": "Saves", "clean_sheets": "Clean sheets", "chance_of_playing_this_round": "Chance to play", "predicted_goals_scored": "Predicted goals", "predicted_assists": "Predicted assists", "predicted_saves": "Predicted saves", "predicted_points_per_game": "Predicted points"}, axis=1)
        self.tempframe = self.dataframe

    def createPlayerTable(self):
        tableframe = self.tempframe
        playertable = pandasModel(tableframe)
        self.playerslayout.setModel(playertable)

    def searchTable(self):
        searchString = self.searchBar.text()
        searchFrame = self.dataframe["Player name"].str.contains(searchString, regex=False)
        searchList = searchFrame.to_list()
        idsList = []
        for i in range(len(searchList)):
            if searchList[i] == True:
                idsList.append(i+1)
        self.tempframe = self.dataframe.query("ID in @idsList")
        self.createPlayerTable()
        self.mainlayout.removeWidget(self.playerslayout)
        self.mainlayout.addWidget(self.playerslayout)