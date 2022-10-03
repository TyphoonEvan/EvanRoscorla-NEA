import pandas as pd
import json
import numpy as np
import requests

pd.options.mode.chained_assignment = None

r = requests.get("https://fantasy.premierleague.com/api/element-summary/158/")
data = json.loads(r.content)
dataframe = pd.json_normalize(data["history"])
refinedframe = dataframe[["element", "total_points", "goals_scored", "assists", "minutes", "round"]]

r = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
data = json.loads(r.content)
playersframe = pd.DataFrame(data["elements"])
teamsframe = pd.DataFrame(data["teams"])
playersubframe = playersframe[["first_name", "second_name", "code", "team", "id", "total_points", "goals_scored", "assists", "minutes", "points_per_game", "saves", "clean_sheets"]]
teamsubframe = teamsframe[["code", "id", "name", "strength_overall_home", "strength_overall_away", "strength_attack_home", "strength_attack_away", "strength_defence_home", "strength_defence_away"]]

def getUsersTeam(user):
    session = requests.session()
    url = "https://users.premierleague.com/accounts/login/"

    headers = {
        'authority': 'users.premierleague.com' ,
        'cache-control': 'max-age=0' ,
        'upgrade-insecure-requests': '1' ,
        'origin': 'https://fantasy.premierleague.com' ,
        'content-type': 'application/x-www-form-urlencoded' ,
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36' ,
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' ,
        'sec-fetch-site': 'same-site' ,
        'sec-fetch-mode': 'navigate' ,
        'sec-fetch-user': '?1' ,
        'sec-fetch-dest': 'document' ,
        'referer': 'https://fantasy.premierleague.com/my-team' ,
        'accept-language': 'en-US,en;q=0.9,he;q=0.8' ,
        }

    payload = {
     "password": "Typhoon1998_",
     "login": "evanroscorla@gmail.com",
     "redirect_uri": "https://fantasy.premierleague.com/a/login",
     "app": "plfpl-web"
    }
    session.post(url, data=payload, headers=headers)
    response = session.get("https://fantasy.premierleague.com/api/my-team/8056230/")
    response = json.loads(response.content)
    userteam = response["picks"]
    userteam = pd.DataFrame(userteam)
    refinedteam = userteam[["element", "position", "is_captain", "is_vice_captain"]]
    teamdict = refinedteam.to_dict()
    return teamdict

def points(dataframe):
    meanpoints = dataframe["total_points"].mean()
    currentpoints = dataframe.iloc[dataframe.shape[0]-1, 1]
    if currentpoints > meanpoints:
        return "+", meanpoints
    elif currentpoints == meanpoints:
        return "=", meanpoints
    else:
        return "-", meanpoints

def trend(dataframe):
    trend = []
    for i in range(dataframe.shape[0]):
        currentval = dataframe.iloc[i, 1]
        try:
            prevval = dataframe.iloc[i-1, 1]
        except IndexError:
            prevval = 0
        difference = currentval-prevval
        trend.append(difference)
    return trend, currentval

def playTime(dataframe):
    averagetime = dataframe["minutes"].mean()
    played = 0
    notplayed = 0
    for i in range(dataframe.shape[0]):
        if dataframe.iloc[i, 4] == 0:
            notplayed+=1
        else:
            played+=1
    return averagetime, played, notplayed

def getPositionDataFrame(dataframe, type):
    positionframe = dataframe[dataframe["element_type"]==type]
    if type == 1:
        positionframe = dataframe[["element_type", "id", "first_name", "second_name", "points_per_game", "total_points", "minutes", "saves", "clean_sheets", "penalties_saved"]]
    elif type == 2:
        positionframe = dataframe[["element_type", "id", "first_name", "second_name", "points_per_game", "total_points", "minutes", "clean_sheets", "goals_scored", "assists"]]
    else:
        positionframe = dataframe[["element_type", "id", "first_name", "second_name", "points_per_game", "total_points", "minutes", "goals_scored", "assists"]]
    return positionframe

def compareRatings(dataframe, player1id, player2id):
    player1 = dataframe[dataframe["id_player"]==player1id]
    player2 = dataframe[dataframe["id_player"]==player2id]
    attack = player1["strength_attack_home"]-player2["strength_defense_away"]
    defense = player1["strength_defense_home"]-player2["strength_attack_away"]
    overall = player1["strength_overall_home"]-player2["strength_overall_away"]
    return attack, defense, overall

def getOverallForm(refinedframe, mergedframe):
    averagecomp, averagepoints = points(refinedframe)
    playertrend, currentpoints = trend(refinedframe)
    averagetime, played, notplayed = playTime(refinedframe)
    averagepointslist = mergedframe["points_per_game"].tolist()
    total = 0
    for i in range(len(averagepointslist)):
        total+=float(averagepointslist[i])
    overallaveragepoints = total/len(averagepointslist)
    averagetotalpoints = mergedframe["total_points"].mean()
    totalplayerpoints = refinedframe.iloc[0, 1]
    comparisonlist = []
    if averagepoints > overallaveragepoints:
        comparisonlist.append("+")
    elif averagepoints == overallaveragepoints:
        comparisonlist.append("=")
    else:
        comparisonlist.append("-")
    if totalplayerpoints > averagetotalpoints:
        comparisonlist.append("+")
    elif totalplayerpoints == averagetotalpoints:
        comparisonlist.append("=")
    else:
        comparisonlist.append("-")
    ups = playertrend.count("+")
    downs = playertrend.count("-")
    averagechange = ups + (downs*(-1))
    if averagechange > 0:
        averagechange = "+"
    elif averagechange == 0:
        averagechange = "="
    else:
        averagechange = "-"
    rating = 50.00 + (16.66*averagechange.count("+") + (-16.66)*averagechange.count("-"))
    rating = rating * (averagetime/90)
    rating = rating * (played/(played+notplayed))
    predictedpoints = currentpoints * (rating+50)
    return rating, predictedpoints

userteam = getUsersTeam("user")
userelements = userteam["element"]
userelementslist = []
for i in range(11):
    userelementslist.append(userelements[i])
playersubframe['picked'] = np.where(playersubframe['id'].isin(userelementslist), True, False)
mergedframe = pd.merge(playersubframe, teamsubframe, left_on='team', right_on='id', suffixes=['_player', '_team'])

print(getOverallForm(refinedframe, mergedframe))