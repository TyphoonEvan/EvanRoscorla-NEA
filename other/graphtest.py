import pandas as pd
import pyqtgraph as pg
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QApplication, QTabWidget
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

        dataframe = pd.read_json("other\\data.json")

        self.mainWidget = MainWidget(self, dataframe)
        self.setCentralWidget(self.mainWidget)
        
        self.show()

class MainWidget(QWidget):
    def __init__(self, parent, dataframe):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.goalkeepers = QWidget()
        self.defenders = QWidget()
        self.midfielders = QWidget()
        self.attackers = QWidget()
        self.tabs.resize(300,200)

        graphsframe = dataframe[["points_per_game", "now_cost", "element_type", "first_name", "second_name"]]

        goalkeepersframe = graphsframe.query("element_type == 1")
        goalkeeperscost = goalkeepersframe["now_cost"].to_list()
        goalkeeperspoints = goalkeepersframe["points_per_game"].to_list()
        goalkeeperfirstnames = goalkeepersframe["first_name"].to_list()
        goalkeepersecondnames = goalkeepersframe["second_name"].to_list()
        goalkeepersnames = []
        for i in range(len(goalkeeperfirstnames)):
            goalkeepersnames.append(goalkeeperfirstnames[i]+" "+goalkeepersecondnames[i])
        goalkeeperscolours = []
        for i in range(len(goalkeeperscost)):
            val = goalkeeperspoints[i]/goalkeeperscost[i]
            if val <= 0:
                goalkeeperscolours.append([255, 87, 51])
            elif val <= 0.065:
                goalkeeperscolours.append([255, 189, 51])
            else:
                goalkeeperscolours.append([117, 255, 51])
        defendersframe = graphsframe.query("element_type == 2")
        defenderscost = defendersframe["now_cost"].to_list()
        defenderspoints = defendersframe["points_per_game"].to_list()
        defenderfirstnames = defendersframe["first_name"].to_list()
        defendersecondnames = defendersframe["second_name"].to_list()
        defendersnames = []
        for i in range(len(defenderfirstnames)):
            defendersnames.append(defenderfirstnames[i]+" "+defendersecondnames[i])
        defenderscolours = []
        for i in range(len(defenderscost)):
            val = defenderspoints[i]/defenderscost[i]
            if val <= 0:
                defenderscolours.append([255, 87, 51])
            elif val <= 0.065:
                defenderscolours.append([255, 189, 51])
            else:
                defenderscolours.append([117, 255, 51])
        midfieldersframe = graphsframe.query("element_type == 3")
        midfielderscost = midfieldersframe["now_cost"].to_list()
        midfielderspoints = midfieldersframe["points_per_game"].to_list()
        midfielderfirstnames = midfieldersframe["first_name"].to_list()
        midfieldersecondnames = midfieldersframe["second_name"].to_list()
        midfieldersnames = []
        for i in range(len(midfielderfirstnames)):
            midfieldersnames.append(midfielderfirstnames[i]+" "+midfieldersecondnames[i])
        midfielderscolours = []
        for i in range(len(midfielderscost)):
            val = midfielderspoints[i]/midfielderscost[i]
            if val <= 0:
                midfielderscolours.append([255, 87, 51])
            elif val <= 0.065:
                midfielderscolours.append([255, 189, 51])
            else:
                midfielderscolours.append([117, 255, 51])
        attackersframe = graphsframe.query("element_type == 4")
        attackerscost = attackersframe["now_cost"].to_list()
        attackerspoints = attackersframe["points_per_game"].to_list()
        attackerfirstnames = attackersframe["first_name"].to_list()
        attackersecondnames = attackersframe["second_name"].to_list()
        attackersnames = []
        for i in range(len(attackerfirstnames)):
            attackersnames.append(attackerfirstnames[i]+" "+attackersecondnames[i])
        attackerscolours = []
        for i in range(len(attackerscost)):
            val = attackerspoints[i]/attackerscost[i]
            if val <= 0:
                attackerscolours.append([255, 87, 51])
            elif val <= 0.065:
                attackerscolours.append([255, 189, 51])
            else:
                attackerscolours.append([117, 255, 51])

        self.tabs.addTab(self.goalkeepers,"Goalkeepers")
        self.tabs.addTab(self.defenders,"Defenders")
        self.tabs.addTab(self.midfielders,"Midfielders")
        self.tabs.addTab(self.attackers,"Attackers")

        self.goalkeepers.layout = QVBoxLayout(self.goalkeepers)
        self.defenders.layout = QVBoxLayout(self.defenders)
        self.midfielders.layout = QVBoxLayout(self.midfielders)
        self.attackers.layout = QVBoxLayout(self.attackers)

        goalkeepersgraph = pg.ScatterPlotItem(size=9)
        goalkeepersplot = pg.plot()
        goalkeepersgraph.setData(goalkeeperscost, goalkeeperspoints, data=goalkeepersnames, brush=goalkeeperscolours, pen="w", hoverable=True, setAcceptHoverEvents=True)
        goalkeepersplot.addItem(goalkeepersgraph)
        goalkeepersplot.setBackground("w")
        goalkeepersplot.setTitle("Points/Cost")
        goalkeepersplot.setLabel("left", "Points")
        goalkeepersplot.setLabel("bottom", "Cost")

        defendersgraph = pg.ScatterPlotItem(size=9)
        defendersplot = pg.plot()
        defendersgraph.setData(defenderscost, defenderspoints, data=defendersnames, brush=defenderscolours, pen="w",  hoverable=True, setAcceptHoverEvents=True)
        defendersplot.addItem(defendersgraph)
        defendersplot.setBackground("w")
        defendersplot.setTitle("Points/Cost")
        defendersplot.setLabel("left", "Points")
        defendersplot.setLabel("bottom", "Cost")

        midfieldersgraph = pg.ScatterPlotItem(size=9)
        midfieldersplot = pg.plot()
        midfieldersgraph.setData(midfielderscost, midfielderspoints, data=midfieldersnames, brush=midfielderscolours, pen="w", hoverable=True, setAcceptHoverEvents=True)
        midfieldersplot.addItem(midfieldersgraph)
        midfieldersplot.setBackground("w")
        midfieldersplot.setTitle("Points/Cost")
        midfieldersplot.setLabel("left", "Points")
        midfieldersplot.setLabel("bottom", "Cost")

        attackersgraph = pg.ScatterPlotItem(size=9)
        attackersplot = pg.plot()
        attackersgraph.setData(attackerscost, attackerspoints, data=attackersnames, brush=attackerscolours, pen="w",  hoverable=True, setAcceptHoverEvents=True)
        attackersplot.addItem(attackersgraph)
        attackersplot.setBackground("w")
        attackersplot.setTitle("Points/Cost")
        attackersplot.setLabel("left", "Points")
        attackersplot.setLabel("bottom", "Cost")

        self.goalkeepers.layout.addWidget(goalkeepersplot)
        self.defenders.layout.addWidget(defendersplot)
        self.midfielders.layout.addWidget(midfieldersplot)
        self.attackers.layout.addWidget(attackersplot) 

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

app = QApplication(sys.argv)
ex = App() 
sys.exit(app.exec_())