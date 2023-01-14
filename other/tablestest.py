from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QTableView, QAbstractScrollArea, QSizePolicy, QHeaderView
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

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Fantasy Premier League"
        self.left = 0
        self.top = 0
        self.width = 1730
        self.height = 800
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.mainWidget = MainWidget(self)
        self.setCentralWidget(self.mainWidget)
        
        self.show()

class MainWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        file = open("data\\bootstrap-static.json", "rb")
        data = file.read()
        data = json.loads(data)
        playersframe = pd.DataFrame(data["elements"])
        playersubframe = playersframe[["first_name", "second_name", "code", "team", "id", "total_points", "goals_scored", "assists", "minutes", "points_per_game", "saves", "clean_sheets", "ict_index", "influence", "creativity", "threat"]]
        dataframe = playersubframe.sort_values("id")
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
        dataframe = pd.concat([dataframe, goals_scored, assists, points, saves, clean_sheets], axis=1)
        self.dataframe = dataframe.loc[:,~dataframe.columns.duplicated(keep="first")].copy()
        self.createPlayerTable()
        self.layout.addWidget(self.playerslayout)


    def createPlayerTable(self):
        tableframe = self.dataframe
        self.playerslayout = QTableView()
        playertable = pandasModel(tableframe)
        self.playerslayout.setModel(playertable)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App() 
    sys.exit(app.exec_())