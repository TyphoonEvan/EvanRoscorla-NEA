import pandas as pd
import pyqtgraph as pg
from PyQt5.QtWidgets import *
import sys
import json

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

        file = open("stylesheet.txt", "r")
        stylesheet = file.read()
        self.setStyleSheet(stylesheet)

        self.graphPage = GraphPage(self)
        self.setCentralWidget(self.graphPage)

        self.show()

class GraphPage(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.mainLayout = QVBoxLayout(self)
        self.selectorLayout = QHBoxLayout(self)

        self.var1Box = QComboBox(self)
        self.var2Box = QComboBox(self)
        self.positionBox = QComboBox(self)

        self.var1Box.currentIndexChanged.connect(self.createGraph)
        self.var2Box.currentIndexChanged.connect(self.createGraph)
        self.positionBox.currentIndexChanged.connect(self.createGraph)

        file = open("data.json", "rb")
        data = file.read()
        data = json.loads(data)
        self.dataframe = pd.DataFrame(data)
        self.dataframe = self.dataframe.drop(["index", "code", "team", "id_avg"], axis=1)
        self.firstnames = self.dataframe["first_name"].to_list()
        self.secondnames = self.dataframe["second_name"].to_list()
        self.fullnames = []
        for i in range(len(self.firstnames)):
            self.fullnames.append(self.firstnames[i] + " " + self.secondnames[i])
        self.dataframe = self.dataframe.drop(["second_name", "predicted_clean_sheets"], axis=1)
        self.dataframe = self.dataframe.replace(self.dataframe["first_name"].values, self.fullnames)
        self.dataframe = self.dataframe.rename({"id": "ID", "first_name": "Player name","total_points": "Total points", "goals_scored": "Goals", "assists": "Assists", "points_per_game": "Points per game", "saves": "Saves", "clean_sheets": "Clean sheets", "chance_of_playing_this_round": "Chance to play", "predicted_goals_scored": "Predicted goals", "predicted_assists": "Predicted assists", "predicted_saves": "Predicted saves", "predicted_points_per_game": "Predicted points"}, axis=1)

        self.selectorVars = self.dataframe.columns
        self.selectorVars = self.selectorVars.to_list()
        self.selectorVars.remove("ID")
        self.selectorVars.remove("Player name")
        self.selectorVars.remove("Chance to play")
        self.selectorVars.remove("now_cost")
        self.selectorVars.remove("element_type")
        self.selectorVars.remove("ict_index")
        self.selectorVars.remove("influence")
        self.selectorVars.remove("creativity")
        self.selectorVars.remove("threat")

        self.var1Box.addItems(self.selectorVars)
        self.var2Box.addItems(self.selectorVars)
        self.positionBox.addItems(["Goalkeepers", "Defenders", "Midfielders", "Attackers"])

        self.graphFrame = self.createGraphFrame()
        self.graph = PandasGraph(self, self.graphFrame).createGraph()

        self.mainLayout.addLayout(self.selectorLayout)
        self.mainLayout.addWidget(self.graph)

        self.selectorLayout.addWidget(self.var1Box)
        self.selectorLayout.addWidget(self.var2Box)
        self.selectorLayout.addWidget(self.positionBox)

    def createGraphFrame(self):
        positions = {"Goalkeepers": 1, "Defenders": 2, "Midfielders": 3, "Attackers": 4}
        var1 = self.var1Box.currentText()
        var2 = self.var2Box.currentText()
        position = self.positionBox.currentText()
        position = positions[position]
        self.graphFrame = self.dataframe.query("element_type == @position")
        xVars = self.graphFrame[var1]
        yVars = self.graphFrame[var2]
        names = self.graphFrame["Player name"]
        self.graphFrame = pd.concat([xVars, yVars, names], axis=1)
        return self.graphFrame
    
    def createGraph(self):
        self.mainLayout.removeWidget(self.graph)
        self.graphFrame = self.createGraphFrame()
        self.graph = PandasGraph(self, self.graphFrame).createGraph()
        self.mainLayout.addWidget(self.graph)

class PandasGraph(QWidget):
    def __init__(self, parent, data):
        super(QWidget, self).__init__(parent)
        self.dataframe = data
    def getXAxis(self):
        return self.dataframe.columns[0]
    def getYAxis(self):
        return self.dataframe.columns[1]
    def getTitle(self):
        xTitle = self.getXAxis()
        yTitle = self.getYAxis()
        return yTitle + "/" + xTitle
    def createGraph(self):
        plot = pg.ScatterPlotItem(size=9)
        graph = pg.plot()
        plot.setData(self.dataframe.iloc[:, 0], self.dataframe.iloc[:, 1], data=self.dataframe.iloc[:, 2], pen="w", hoverable=True, setAcceptHoverEvents=True)
        graph.addItem(plot)
        graph.setBackground("black")
        graph.setTitle(self.getTitle())
        graph.setLabel("left", self.getYAxis())
        graph.setLabel("bottom", self.getXAxis())
        return graph

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())