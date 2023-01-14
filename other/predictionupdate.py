import pandas as pd
import json
import numpy as np
import requests
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import itertools
import time

def getPlayerData(playerid):
    r = requests.get("https://fantasy.premierleague.com/api/element-summary/"+playerid+"/")
    data = json.loads(r.content)
    dataframe = pd.json_normalize(data["history"])
    playerhistory = dataframe[["element", "total_points", "goals_scored", "assists", "minutes", "saves", "clean_sheets", "ict_index", "influence", "creativity", "threat", "round"]]
    playerhistory = playerhistory.rename({"total_points": "points_per_game"}, axis=1)

    r = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    data = json.loads(r.content)
    playersframe = pd.DataFrame(data["elements"])
    playersubframe = playersframe[["first_name", "second_name", "code", "team", "id", "total_points", "goals_scored", "assists", "minutes", "points_per_game", "saves", "clean_sheets", "ict_index", "influence", "creativity", "threat", "element_type"]]
    playersubframe = playersubframe.sort_values("id")
    playerinfo = playersubframe.iloc[int(playerid)-1]

    return playerinfo, playerhistory

def calculatePlayTime(playerinfo, totalgames):
    totaltime = playerinfo["minutes"]
    return totaltime/totalgames

def getTeamData(playerteam):
    r = requests.get("https://fantasy.premierleague.com/api/fixtures")
    data = json.loads(r.content)
    dataframe = pd.DataFrame(data)
    dataframe = dataframe[dataframe["finished"]==True]
    fixtures = dataframe[["team_h", "team_a", "event"]]
    homes = fixtures[dataframe["team_h"]==playerteam]
    aways = fixtures[dataframe["team_a"]==playerteam]

    r = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    data = json.loads(r.content)
    dataframe = pd.DataFrame(data["teams"])
    teams = dataframe[["code", "id", "name", "strength_overall_home", "strength_overall_away", "strength_attack_home", "strength_attack_away", "strength_defence_home", "strength_defence_away"]]
    
    return homes, aways, teams

def getPrediction(df):
    matrix = np.array(df.values,"int")
    x = matrix[:,0].reshape((-1,1))
    y = matrix[:,1]
    model = LinearRegression()
    model.fit(x,y)
    return model.intercept_, model.coef_

def getCurrentGameweek(gameweeks):
    for i in range(len(gameweeks.index)):
        if gameweeks.iloc[i, 4] == False:
            return i+1

def predictPerformance(id):
    playerinfo, playerhistory = getPlayerData(str(id))
    stats = ["goals_scored", "assists", "saves", "clean_sheets", "points_per_game"]
    intercepts = []
    coefs = []
    for i in range(len(stats)):
        currentstat = stats[i]
        vallist = []
        prevval = 0
        df = playerhistory[[currentstat, "round"]]
        for j in range(len(df.index)):
            currentval = df.iloc[j ,0]
            currentval += prevval
            vallist.append(currentval)
            prevval = currentval
        df = pd.concat([df, pd.Series(vallist)], axis=1)
        df = df.drop(currentstat, axis=1)
        intercept, coef = getPrediction(df)
        coef = coef[0]
        intercepts.append(intercept)
        coefs.append(coef)
    predictiontable = pd.DataFrame({"intercept": intercepts, "coef": coefs}, index = stats)
    return predictiontable

r = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
data = json.loads(r.content)
playersframe = pd.DataFrame(data["elements"])
gameweeks = pd.DataFrame(data["events"])
playersubframe = playersframe[["first_name", "second_name", "code", "team", "id", "total_points", "goals_scored", "assists", "minutes", "points_per_game", "saves", "clean_sheets", "ict_index", "influence", "creativity", "threat", "now_cost", "element_type", "chance_of_playing_this_round"]]
playersubframe = playersubframe.sort_values("id")
currentgameweek = getCurrentGameweek(gameweeks)

predictiontable = predictPerformance(687)
print(predictiontable)