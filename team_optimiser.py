import pandas as pd
import json
import numpy as np
import requests
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import itertools
import time

class PerformancePredictor():
    def __init__(self, playerhistory):
        self.playerhistory = playerhistory
    
    @staticmethod
    def getPrediction(df):
        '''Uses linear regression to predict a players future performance, takes dataframe, returns 2 floats'''
        matrix = np.array(df.values,"int")
        x = matrix[:,0].reshape((-1,1))
        y = matrix[:,1]
        model = LinearRegression()
        model.fit(x,y)
        return model.intercept_, model.coef_

    def predictPerformance(self):
        '''Predicts the performance of a player, returns dataframe'''
        stats = ["goals_scored", "assists", "saves", "clean_sheets", "points_per_game"]
        intercepts = []
        coefs = []
        for i in range(len(stats)):
            currentstat = stats[i]
            vallist = []
            prevval = 0
            df = self.playerhistory[[currentstat, "round"]]
            for j in range(len(df.index)):
                currentval = df.iloc[j ,0]
                currentval += prevval
                vallist.append(currentval)
                prevval = currentval
            df = pd.concat([df, pd.Series(vallist)], axis=1)
            df = df.drop(currentstat, axis=1)
            intercept, coef = self.getPrediction(df)
            coef = coef[0]
            intercepts.append(intercept)
            coefs.append(coef)
        predictiontable = pd.DataFrame({"intercept": intercepts, "coef": coefs}, index = stats)
        return predictiontable

class TeamOptimiser():
    def __init__(self):
        pass

    def prepareData(self):
        file = open("data.json", "r")
        data = file.read()
        file.close()
        data = json.loads(data)
        dataframe = pd.DataFrame(data)
        columns = list(dataframe.columns)

        dataframe = dataframe.query("chance_of_playing_this_round >= 30")
        dataframe = dataframe.query("average_play_time >= 20")

        goalkeepers = dataframe.query("element_type == 1")
        topgoalkeepers = goalkeepers.query("now_cost <= 40 and now_cost > 30")
        topgoalkeepers = topgoalkeepers.sort_values(columns[3], ascending=False)
        topgoalkeepers = topgoalkeepers.head(1)

        defenders = dataframe.query("element_type == 2")
        topdefenders = defenders.query("now_cost <= 40 and now_cost > 30")
        topdefenders = topdefenders.sort_values(columns[3], ascending=False)
        topdefenders = topdefenders.head(2)

        midfielders = dataframe.query("element_type == 3")
        topmidfielders = midfielders.query("now_cost <= 40 and now_cost > 30")
        topmidfielders = topmidfielders.sort_values(columns[3], ascending=False)
        topmidfielders = topmidfielders.head(1)

        attackers = dataframe.query("element_type == 4")
        topattackers = attackers.query("now_cost <= 40 and now_cost > 30")
        topattackers = topattackers.sort_values(columns[3], ascending=False)
        topattackers = topattackers.head(1)

        for i in range(9):
           mincost = (i+4)*10
           maxcost = mincost+10
           players = goalkeepers.query("now_cost <= @maxcost and now_cost > @mincost")
           players = players.sort_values(columns[3], ascending=False)
           players = players.head(1)
           topgoalkeepers = pd.concat([topgoalkeepers, players], axis=0)
        empty = []
        for i in range(len(topgoalkeepers.index)):
            if topgoalkeepers.iloc[i, 0] == "{}":
                empty.append(i)
        self.topgoalkeepers = topgoalkeepers.drop(empty)

        for i in range(9):
           mincost = (i+4)*10
           maxcost = mincost+10
           players = defenders.query("now_cost <= @maxcost and now_cost > @mincost")
           players = players.sort_values(columns[3], ascending=False)
           players = players.head(2)
           topdefenders = pd.concat([topdefenders, players], axis=0)
        empty = []
        for i in range(len(topdefenders.index)):
            if topdefenders.iloc[i, 0] == "{}":
                empty.append(i)
        self.topdefenders = topdefenders.drop(empty)

        for i in range(9):
           mincost = (i+4)*10
           maxcost = mincost+10
           players = midfielders.query("now_cost <= @maxcost and now_cost > @mincost")
           players = players.sort_values(columns[3], ascending=False)
           players = players.head(1)
           topmidfielders = pd.concat([topmidfielders, players], axis=0)
        empty = []
        for i in range(len(topmidfielders.index)):
            if topmidfielders.iloc[i, 0] == "{}":
                empty.append(i)
        self.topmidfielders = topmidfielders.drop(empty)

        for i in range(9):
           mincost = (i+4)*10
           maxcost = mincost+10
           players = attackers.query("now_cost <= @maxcost and now_cost > @mincost")
           players = players.sort_values(columns[3], ascending=False)
           players = players.head(1)
           topattackers = pd.concat([topattackers, players], axis=0)
        empty = []
        for i in range(len(topattackers.index)):
            if topattackers.iloc[i, 0] == "{}":
                empty.append(i)
        self.topattackers = topattackers.drop(empty)

    def checkTeam(self, team, topteampoints):
        '''Tests the currently selected team against the current best, takes dataframe and int, returns 2 ints'''
        if len(team.index) < 11:
            return -1, 0
        teamcost = 0
        for i in range(11):
            teamcost += team.iloc[i, 17]
        if teamcost > 1000:
            return -1, 0
        else:
            teampoints = 0
            for j in range(11):
                teampoints += float(team.iloc[j, 5])
            if teampoints > topteampoints:
                return 1, teampoints
            else:
                return -1, teampoints
    
    def loopDefenders(self, team, topteampoints, topteam):
        '''Selects a set of defenders and adds them to the current team, takes 2 dataframes and int, returns dataframe and int'''
        oldteam = team
        for i in range(len(self.alldefenders)):
            team = oldteam
            currentdefenders = self.alldefenders[i]
            for j in range(5):
                id = currentdefenders[j]
                team = pd.concat([team, self.topdefenders.query("id == @id")], axis=0)
            topteam, topteampoints = self.loopMidfielders(team, topteampoints, topteam)
        return topteam, topteampoints
    
    def loopMidfielders(self, team, topteampoints, topteam):
        '''Selects a set of midfielders and adds them to the current team, takes 2 dataframes and int, returns dataframe and int'''
        oldteam = team
        for i in range(len(self.allmidfielders)):
            team = oldteam
            currentmidfielders = self.allmidfielders[i]
            for j in range(3):
                id = currentmidfielders[j]
                team = pd.concat([team, self.topmidfielders.query("id == @id")], axis=0)
            topteam, topteampoints = self.loopAttackers(team, topteampoints, topteam)
        return topteam, topteampoints
    
    def loopAttackers(self, team, topteampoints, topteam):
        '''Selects a set of attackers and adds them to the current team, takes 2 dataframes and int, returns dataframe and int'''
        oldteam = team
        print("done")
        for i in range(len(self.allattackers)):
            team = oldteam
            currentattackers = self.allattackers[i]
            for j in range(2):
                id = currentattackers[j]
                team = pd.concat([team, self.topattackers.query("id == @id")], axis=0)
            passed, teampoints = self.checkTeam(team, topteampoints)
            if passed == 1:
                topteampoints = teampoints
                topteam = team
        return topteam, topteampoints

    def calculateTeam(self):
        topteampoints = 0
        defenderslist = []
        for i in range(len(self.topdefenders.index)):
            defenderslist.append(self.topdefenders.iloc[i, 1])
        self.alldefenders = []
        for subset in itertools.combinations(defenderslist, 5): self.alldefenders.append(subset)
        midfielderslist = []
        for i in range(len(self.topmidfielders.index)):
            midfielderslist.append(self.topmidfielders.iloc[i, 1])
        self.allmidfielders = []
        for subset in itertools.combinations(midfielderslist, 3): self.allmidfielders.append(subset)
        attackerslist = []
        for i in range(len(self.topattackers.index)):
            attackerslist.append(self.topattackers.iloc[i, 1])
        self.allattackers = []
        for subset in itertools.combinations(attackerslist, 2): self.allattackers.append(subset)
        topteam = ""
        goalkeeperslist = []
        for i in range(len(self.topgoalkeepers.index)):
            goalkeeperslist.append(self.topgoalkeepers.iloc[i, 1])
        for i in range(len(self.topgoalkeepers.index)):
            id = goalkeeperslist[i]
            currentgoalkeeper = self.topgoalkeepers.query("id == @id")
            team = currentgoalkeeper
            topteam, topteampoints = self.loopDefenders(team, topteampoints, topteam)
        return topteam