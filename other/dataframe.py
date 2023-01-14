import json
import pandas as pd
import requests

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

def calculatePlayTime(playerhistory):
    totaltime = 0
    totalgames = 0
    for i in range(len(playerhistory.index)):
        totaltime += playerhistory.iloc[i, 4]
        totalgames += 1
        print(totaltime)
    averagetime = totaltime/totalgames
    return averagetime

playerinfo, playerhistory = getPlayerData("176")
print(playerhistory)
print(calculatePlayTime(playerhistory))