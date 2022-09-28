import pandas as pd
import json
import numpy as np
import requests

r = requests.get("https://fantasy.premierleague.com/api/element-summary/158/")
data = json.loads(r.content)
dataframe = pd.json_normalize(data["history"])
refinedframe = dataframe[["element", "total_points", "goals_scored", "assists", "minutes", "round"]]

def points(dataframe):
    meanpoints = dataframe["total_points"].mean()
    currentpoints = dataframe.iloc[dataframe.shape[0], 1]
    if currentpoints > meanpoints:
        return "+"
    elif currentpoints == meanpoints:
        return "="
    else:
        return "-"

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
    return trend

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