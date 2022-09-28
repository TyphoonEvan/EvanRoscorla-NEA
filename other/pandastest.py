import pandas as pd
import json
import numpy as np
import requests

r = requests.get("https://fantasy.premierleague.com/api/element-summary/158/")
data = json.loads(r.content)
dataframe = pd.json_normalize(data["history"])
refinedframe = dataframe[["element", "total_points", "goals_scored", "assists", "minutes", "round"]]

def getPoints(dataframe):
    meanpoints = dataframe["total_points"].mean()
    currentpoints = dataframe.iloc[dataframe.shape[0]-1, 1]
    if currentpoints > meanpoints:
        return "+"
    elif currentpoints == meanpoints:
        return "="
    else:
        return "-"

print(getPoints(refinedframe))

def getTrend(dataframe):
    trend = []
    for i in range(dataframe.shape[0]-1):
        currentval = dataframe.iloc[i, 1]
        try:
            prevval = dataframe.iloc[i-1, 1]
        except IndexError:
            prevval = 0
        difference = currentval-prevval
        trend.append(difference)
    return trend

print(getTrend(refinedframe))