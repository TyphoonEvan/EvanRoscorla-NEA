import pandas as pd
import json
import numpy as np
import requests

r = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
data = json.loads(r.content)
playersframe = pd.DataFrame(data["elements"])
playersubframe = playersframe[["first_name", "second_name", "code", "team", "id", "total_points", "goals_scored", "assists", "minutes", "points_per_game", "saves", "clean_sheets", "ict_index", "influence", "creativity", "threat"]]
dataframe = playersubframe.sort_values("id")
file = open("data\\goals_scored.json", "r")
data = file.read()
goals_scored = pd.read_json(data)
file.close()
file = open("data\\assists.json", "r")
data = file.read()
assists = pd.read_json(data)
file.close()
file = open("data\\points.json", "r")
data = file.read()
points = pd.read_json(data)
file.close()
file = open("data\\saves.json", "r")
data = file.read()
saves = pd.read_json(data)
file.close()
file = open("data\\clean_sheets.json", "r")
data = file.read()
clean_sheets = pd.read_json(data)
file.close()
dataframe = pd.concat([dataframe, goals_scored, assists, points, saves, clean_sheets], axis=1)
dataframe = dataframe.loc[:,~dataframe.columns.duplicated(keep="first")].copy()