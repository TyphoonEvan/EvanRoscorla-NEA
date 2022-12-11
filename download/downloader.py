import requests
import json
import pandas as pd
from cryptography.fernet import Fernet
import ast

class AutoDownloader():
    def downloadGenericData(gameweek):
        file = open("config\\download_config.json", "r")
        data = file.read()
        config = json.loads(data)
        file.close()
        for i in range(len(config)):
            url = config[i].get("url")
            if "{event_id}" in url:
                url = url.replace("{event_id}", str(gameweek))
            response = requests.get(url)
            filename = "data\\"+config[i].get("name")+".json"
            file = open(filename, "wb")
            file.write(response.content)
            file.close()

    def getPlayersFrame():
        file = open("data\\bootstrap-static.json", "rb")
        data = file.read()
        data = json.loads(data)
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
        return dataframe

    def getTeamsFrame():
        file = open("data\\bootstrap-static.json", "rb")
        data = file.read()
        data = json.loads(data)
        file.close()
        dataframe = pd.DataFrame(data["teams"])
        dataframe = dataframe[["code", "id", "name", "strength_overall_home", "strength_overall_away", "strength_attack_home", "strength_attack_away", "strength_defence_home", "strength_defence_away"]]
        return dataframe

    def getUserData(user):
        file = open("key.key", "rb")
        key = file.read()
        file.close()
        f = Fernet(key)

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

        file = open("config\\"+user+".cnfg", "rb")
        data = file.read()
        data = f.decrypt(data).decode("utf-8")
        file.close()
        data = ast.literal_eval(data)
        password = data.get("password")
        username = data.get("username")
        id = data.get("manager_id")

        payload = {
         "password": password,
         "login": username,
         "redirect_uri": "https://fantasy.premierleague.com/a/login",
         "app": "plfpl-web"
        }
        print(payload)

        session.post(url, data=payload, headers=headers)
        response = session.get("https://fantasy.premierleague.com/api/my-team/"+id+"/")
        response = json.loads(response.content)
        userteam = response["picks"]
        userteam = pd.DataFrame(userteam)
        refinedteam = userteam[["element", "position", "is_captain", "is_vice_captain"]]
        teamdict = refinedteam.to_dict()
        return teamdict