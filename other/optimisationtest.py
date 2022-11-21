import pandas as pd
import json
import numpy as np
import requests
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import itertools
import time

def getPlayerData(playerid):
    print(playerid)
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
        if gameweeks.iloc[i, 4] == "true":
            return i+1

def compareTeams(teams, homeid, awayid):
    hometeam = teams.iloc[homeid-1,:]
    awayteam = teams.iloc[awayid-1,:]
    attackdif = hometeam["strength_attack_home"] - awayteam["strength_defence_away"]
    defensedif = hometeam["strength_defence_home"] - awayteam["strength_attack_away"]
    overalldif = hometeam["strength_overall_home"] - awayteam["strength_overall_away"]
    return attackdif, defensedif, overalldif

def getPlayerDataframe(stat):
    r = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    data = json.loads(r.content)
    playersframe = pd.DataFrame(data["elements"])
    gameweeks = pd.DataFrame(data["events"])
    playersubframe = playersframe[["first_name", "second_name", "code", "team", "id", "total_points", "goals_scored", "assists", "minutes", "points_per_game", "saves", "clean_sheets", "ict_index", "influence", "creativity", "threat", "now_cost", "element_type"]]
    playersubframe = playersubframe.sort_values("id")

    r = requests.get("https://fantasy.premierleague.com/api/fixtures")
    data = json.loads(r.content)
    fixtures = pd.DataFrame(data)
    fixtures = fixtures[fixtures["finished"]==False]
    hometeams = fixtures["team_h"].to_list()
    awayteams = fixtures["team_a"].to_list()
    currentgameweek = getCurrentGameweek(gameweeks)

    attacks = ["goals_scored", "assists"]
    defenses = ["saves", "clean_sheets"]
    overalls = ["points_per_game", "ict_index", "influence", "creativity", "threat"]

    predictedstatlist = []
    for i in range(len(playersubframe.index)):
        currentplayer = playersubframe.iloc[i, :]
        playerinfo, playerhistory = getPlayerData(str(currentplayer["id"]))
        homes, aways, teams = getTeamData(currentplayer["team"])
        prevfixtures = pd.concat([homes, aways])
        prevfixtures = prevfixtures.sort_values("event")
        difs = []
        for j in range(len(prevfixtures.index)):
            homeid = prevfixtures.iloc[j, 0]
            awayid = prevfixtures.iloc[j, 1]
            attackdif, defensedif, overalldif = compareTeams(teams, homeid, awayid)
            if awayid == currentplayer["team"]:
                overalldif = overalldif*(-1)
                attackdif = attackdif*(-1)
                defensedif = defensedif*(-1)
            if stat in attacks:
                difs.append(attackdif)
                diftype = "attack_dif"
            elif stat in defenses:
                difs.append(defensedif)
                diftype = "defense_dif"
            elif stat in overalls:
                difs.append(overalldif)
                diftype = "overall_dif"
        difs = pd.Series(difs)
        playerhistory = pd.concat([playerhistory, difs], axis=1)
        playerhistory = playerhistory.rename(columns={0: diftype}).dropna()
        playerhistory = playerhistory[[diftype, stat]]
        intercept, coef = getPrediction(playerhistory)
        if currentplayer["team"] in hometeams:
            pos = hometeams.index(currentplayer["team"])
            opp = awayteams[pos]
            attackdif, defensedif, overalldif = compareTeams(teams, currentplayer["team"], opp)
        elif currentplayer["team"] in awayteams:
            pos = awayteams.index(currentplayer["team"])
            opp = hometeams[pos]
            attackdif, defensedif, overalldif = compareTeams(teams, opp, currentplayer["team"])
        if stat in attacks:
            predictedstat = (attackdif*coef) + intercept
        elif stat in defenses:
            predictedstat = (defensedif*coef) + intercept
        elif stat in overalls:
            predictedstat = (overalldif*coef) + intercept
        predictedstatlist.append(round(float(predictedstat)))
    predictedstat = pd.Series(predictedstatlist)
    dataframe = pd.concat([playersubframe, predictedstat], axis=1)
    dataframe = dataframe[["id", "first_name", "second_name", stat, "now_cost", "element_type"]]
    return dataframe

file = open("other\\data.json", "r")
data = file.read()
file.close()
data = json.loads(data)
dataframe = pd.DataFrame(data)
columns = list(dataframe.columns)
goalkeepers = dataframe.query("element_type == 1")
topgoalkeepers = goalkeepers.query("now_cost <= 40 and now_cost > 30")
topgoalkeepers = topgoalkeepers.sort_values(columns[3], ascending=False)
topgoalkeepers = topgoalkeepers.head(1)
defenders = dataframe.query("element_type == 2")
topdefenders = defenders.query("now_cost <= 40 and now_cost > 30")
topdefenders = topdefenders.sort_values(columns[3], ascending=False)
topdefenders = topdefenders.head(3)
midfielders = dataframe.query("element_type == 3")
topmidfielders = midfielders.query("now_cost <= 40 and now_cost > 30")
topmidfielders = topmidfielders.sort_values(columns[3], ascending=False)
topmidfielders = topmidfielders.head(2)
attackers = dataframe.query("element_type == 4")
topattackers = attackers.query("now_cost <= 40 and now_cost > 30")
topattackers = topattackers.sort_values(columns[3], ascending=False)
topattackers = topattackers.head(2)
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
topgoalkeepers = topgoalkeepers.drop(empty)

for i in range(9):
   mincost = (i+4)*10
   maxcost = mincost+10
   players = defenders.query("now_cost <= @maxcost and now_cost > @mincost")
   players = players.sort_values(columns[3], ascending=False)
   players = players.head(1)
   topdefenders = pd.concat([topdefenders, players], axis=0)
empty = []
for i in range(len(topdefenders.index)):
    if topdefenders.iloc[i, 0] == "{}":
        empty.append(i)
topdefenders = topdefenders.drop(empty)

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
topmidfielders = topmidfielders.drop(empty)

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
topattackers = topattackers.drop(empty)

def checkTeam(team, topteampoints):
    if len(team.index) < 11:
        return -1, 0
    teamcost = 0
    for i in range(11):
        teamcost += team.iloc[i, 4]
    if teamcost > 1000:
        return -1
    else:
        teampoints = 0
        for j in range(11):
            teampoints += float(team.iloc[j, 3])
        if teampoints > topteampoints:
            return 1, teampoints
        else:
            return -1, teampoints

def loopDefenders(team, topteampoints, topteam):
    oldteam = team
    for i in range(len(alldefenders)):
        team = oldteam
        currentdefenders = alldefenders[i]
        for j in range(5):
            id = currentdefenders[j]
            team = pd.concat([team, topdefenders.query("id == @id")], axis=0)
        topteam, topteampoints = loopMidfielders(team, topteampoints, topteam)
    return topteam, topteampoints

def loopMidfielders(team, topteampoints, topteam):
    oldteam = team
    for i in range(len(allmidfielders)):
        team = oldteam
        currentmidfielders = allmidfielders[i]
        for j in range(3):
            id = currentmidfielders[j]
            team = pd.concat([team, topmidfielders.query("id == @id")], axis=0)
        topteam, topteampoints = loopAttackers(team, topteampoints, topteam)
    return topteam, topteampoints

def loopAttackers(team, topteampoints, topteam):
    oldteam = team
    for i in range(len(allattackers)):
        team = oldteam
        currentattackers = allattackers[i]
        for j in range(2):
            id = currentattackers[j]
            team = pd.concat([team, topattackers.query("id == @id")], axis=0)
        passed, teampoints = checkTeam(team, topteampoints)
        if passed == 1:
            topteampoints = teampoints
            topteam = team
    return topteam, topteampoints

topteampoints = 0
defenderslist = []
for i in range(len(topdefenders.index)):
    defenderslist.append(topdefenders.iloc[i, 0])
alldefenders = []
for subset in itertools.combinations(defenderslist, 5): alldefenders.append(subset)
midfielderslist = []
for i in range(len(topmidfielders.index)):
    midfielderslist.append(topmidfielders.iloc[i, 0])
allmidfielders = []
for subset in itertools.combinations(midfielderslist, 3): allmidfielders.append(subset)
attackerslist = []
for i in range(len(topattackers.index)):
    attackerslist.append(topattackers.iloc[i, 0])
allattackers = []
for subset in itertools.combinations(attackerslist, 2): allattackers.append(subset)
topteam = ""
goalkeeperslist = []
for i in range(len(topgoalkeepers.index)):
    goalkeeperslist.append(topgoalkeepers.iloc[i, 0])
for i in range(len(topgoalkeepers.index)):
    id = goalkeeperslist[i]
    currentgoalkeeper = topgoalkeepers.query("id == @id")
    team = currentgoalkeeper
    topteam, topteampoints = loopDefenders(team, topteampoints, topteam)
print(topteam)