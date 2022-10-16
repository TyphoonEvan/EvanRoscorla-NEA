import pandas as pd
import json
import numpy as np
import requests
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

pd.options.mode.chained_assignment = None

def getPlayerData(playerid):
    r = requests.get("https://fantasy.premierleague.com/api/element-summary/"+playerid+"/")
    data = json.loads(r.content)
    dataframe = pd.json_normalize(data["history"])
    playerhistory = dataframe[["element", "total_points", "goals_scored", "assists", "minutes", "saves", "clean_sheets", "ict_index", "influence", "creativity", "threat", "round"]]

    r = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    data = json.loads(r.content)
    playersframe = pd.DataFrame(data["elements"])
    playersubframe = playersframe[["first_name", "second_name", "code", "team", "id", "total_points", "goals_scored", "assists", "minutes", "points_per_game", "saves", "clean_sheets", "ict_index", "influence", "creativity", "threat"]]
    playersubframe = playersubframe.sort_values("id")
    playerinfo = playersubframe.iloc[int(playerid)-1]

    return playerinfo, playerhistory

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

def compareTeams(teams, homeid, awayid):
    hometeam = teams.iloc[homeid-1,:]
    awayteam = teams.iloc[awayid-1,:]
    attackdif = hometeam["strength_attack_home"] - awayteam["strength_defence_away"]
    defensedif = hometeam["strength_defence_home"] - awayteam["strength_attack_away"]
    return attackdif, defensedif

def calculateRatio(stat, stattype, playerhistory, teams, homes, aways, playerteam, location):
    ratios = []
    if location == "home":
        for i in range(len(homes.index)):
            opp = homes.iloc[i, 1]
            attackdif, defensedif = compareTeams(teams, playerteam, opp)
            gameweek = homes.iloc[i, 2]
            playerstats = playerhistory.loc[playerhistory["round"]==gameweek]
            statval = playerstats[stat].min()
            if stattype == "attack":
                ratios.append(statval/attackdif)
            else:
                ratios.append(statval/defensedif)
    else:
        for i in range(len(aways.index)):
            opp = homes.iloc[i, 0]
            attackdif, defensedif, overalldif = compareTeams(teams, opp, playerteam)
            #reverses equations
            attackdif = attackdif*(-1)
            defensedif = defensedif*(-1)
            overalldif = overalldif*(-1)
            if stattype == "attack":
                ratios.append(statval/attackdif)
            else:
                ratios.append(statval/defensedif)
    meanratio = sum(ratios)/(len(ratios)+1)
    return meanratio

def getLinearRegression(playerhistory, currentvar):
    attacktype = ["goals_scored", "assists"]
    defensetype = ["saves", "clean_sheets"]
    if currentvar in attacktype:
        df = playerhistory[["attack_dif", currentvar]]
        matrix = np.array(df.values,"int")
        x = matrix[:,0].reshape((-1,1))
        y = matrix[:,1]
        model = LinearRegression()
        model.fit(x,y)
        return model.intercept_, model.coef_

def getCorrelation(playerid, playerteam):
    playerinfo, playerhistory = getPlayerData(str(playerid))
    homes, aways, teams = getTeamData(playerteam)
    fixtures = pd.concat([homes, aways])
    fixtures = fixtures.sort_values("event")
    print(fixtures)
    attack = []
    defense = []
    for i in range(len(fixtures.index)):
        homeid = fixtures.iloc[i, 0]
        awayid = fixtures.iloc[i, 1]
        attackdif, defensedif = compareTeams(teams, homeid, awayid)
        if awayid == playerteam:
            attackdif = attackdif*(-1)
            defensedif = defensedif*(-1)
        attack.append(attackdif)
        defense.append(defensedif)
    attack = pd.Series(attack)
    defense = pd.Series(defense)
    playerhistory = pd.concat([playerhistory, attack, defense], axis=1)
    playerhistory = playerhistory.rename(columns={0: "attack_dif", 1: "defense_dif"}).dropna()
    corr = playerhistory.corr()
    corr = corr.drop(["element", "saves", "attack_dif", "defense_dif", "round", "total_points"], axis=0)
    corr = corr.drop(["element", "total_points", "goals_scored", "assists", "minutes", "clean_sheets", "round", "saves"], axis=1)
    return corr, playerhistory