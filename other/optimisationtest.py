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

def compareTeams(teams, homeid, awayid):
    hometeam = teams.iloc[homeid-1,:]
    awayteam = teams.iloc[awayid-1,:]
    attackdif = hometeam["strength_attack_home"] - awayteam["strength_defence_away"]
    defensedif = hometeam["strength_defence_home"] - awayteam["strength_attack_away"]
    overalldif = hometeam["strength_overall_home"] - awayteam["strength_overall_away"]
    return attackdif, defensedif, overalldif

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

def getPlayerDataframe():
    r = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    data = json.loads(r.content)
    playersframe = pd.DataFrame(data["elements"])
    gameweeks = pd.DataFrame(data["events"])
    playersubframe = playersframe[["id", "first_name", "second_name", "code", "team", "total_points", "goals_scored", "assists", "minutes", "points_per_game", "saves", "clean_sheets", "ict_index", "influence", "creativity", "threat", "now_cost", "element_type", "chance_of_playing_this_round"]]
    playersubframe = playersubframe.sort_values("id")

    r = requests.get("https://fantasy.premierleague.com/api/fixtures")
    data = json.loads(r.content)
    fixtures = pd.DataFrame(data)
    fixtures = fixtures[fixtures["finished"]==False]
    hometeams = fixtures["team_h"].to_list()
    awayteams = fixtures["team_a"].to_list()
    currentgameweek = getCurrentGameweek(gameweeks)

    averages = []
    predictedstatframe = pd.DataFrame()
    idslist = []
    for i in range(len(playersubframe.index)):
        currentplayer = playersubframe.iloc[i, :]
        idslist.append(currentplayer["id"])
        playerinfo, playerhistory = getPlayerData(str(currentplayer["id"]))
        averagetime = calculatePlayTime(playerinfo, currentgameweek)
        averages.append(averagetime)
        predictiontable = predictPerformance(currentplayer["id"])
        predictionlist = []
        for j in range(len(predictiontable.index)):
            predictionlist.append((currentgameweek * predictiontable.iloc[j, 1]) + predictiontable.iloc[j, 0])
        predictionlist = pd.Series(predictionlist)
        predictedstatframe = pd.concat([predictedstatframe, predictionlist], axis=1)
        predictedstatframe = predictedstatframe.rename({0: i+1}, axis=1)
    predictedstatframe = predictedstatframe.transpose()
    idsseries = pd.Series(idslist)
    predictedstatframe = pd.concat([predictedstatframe, idsseries], axis=1)
    averages = {idslist[i]: averages[i] for i in range(len(idslist))}
    averages = pd.DataFrame(list(averages.items()), columns=["id", "average_play_time"])
    print(averages)
    predictedstatframe = predictedstatframe.rename({0: "predicted_goals_scored", 1: "predicted_assists", 2: "predicted_saves", 3: "predicted_clean_sheets", 4: "predicted_points_per_game", 5: "id"}, axis=1)
    dataframe = playersubframe.join(predictedstatframe, on="id")
    dataframe = dataframe.reset_index()
    dataframe = dataframe.join(averages, rsuffix="_avg")
    return dataframe

dataframe = getPlayerDataframe()
file = open("other\\data.json", "w")
file.write(json.dumps(dataframe.to_dict()))
file.close()
print(dataframe)
exit()
file = open("other\\data.json", "r")
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
topgoalkeepers = topgoalkeepers.drop(empty)

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
        teamcost += team.iloc[i, 16]
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
    print("done")
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