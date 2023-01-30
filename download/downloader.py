import requests
import json
import pandas as pd
from cryptography.fernet import Fernet
import ast
from team_optimiser import PerformancePredictor

class AutoDownloader():
    def downloadGenericData(gameweek):
        '''Downloads the general data'''
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

    def getPlayerDataframe(self):
        '''Creates the dataframe of all players and stats, returns dataframe'''
        file = open("data\\bootstrap-static.json", "rb")
        data = file.read()
        file.close()
        data = json.loads(data)
        playersframe = pd.DataFrame(data["elements"])
        gameweeks = pd.DataFrame(data["events"])
        playersubframe = playersframe[["id", "first_name", "second_name", "code", "team", "total_points", "goals_scored", "assists", "minutes", "points_per_game", "saves", "clean_sheets", "ict_index", "influence", "creativity", "threat", "now_cost", "element_type", "chance_of_playing_this_round"]]
        playersubframe = playersubframe.sort_values("id")

        currentgameweek = getCurrentGameweek(gameweeks)

        averages = []
        predictedstatframe = pd.DataFrame()
        idslist = []
        for i in range(len(playersubframe.index)):
            currentplayer = playersubframe.iloc[i, :]
            currentid = currentplayer["id"]
            playerdownloader = PlayerDownloader(currentid, currentgameweek)
            idslist.append(currentid)
            playerinfo, playerhistory = playerdownloader.getPlayerData()
            averagetime = playerdownloader.calculatePlayTime()
            averages.append(averagetime)
            performancePredictor = PerformancePredictor(playerhistory)
            predictiontable = performancePredictor.predictPerformance()
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
        predictedstatframe = predictedstatframe.rename({0: "predicted_goals_scored", 1: "predicted_assists", 2: "predicted_saves", 3: "predicted_clean_sheets", 4: "predicted_points_per_game", 5: "id"}, axis=1)
        dataframe = playersubframe.join(predictedstatframe, on="id")
        dataframe = dataframe.reset_index()
        dataframe = dataframe.join(averages, rsuffix="_avg")
        file = open("data\\player-data.json", "w")
        file.write(json.dumps(dataframe.to_dict()))
        file.close()

    def getTeamsFrame(self):
        '''Downloads team specific data, returns a dataframe'''
        file = open("data\\bootstrap-static.json", "rb")
        data = file.read()
        data = json.loads(data)
        file.close()
        dataframe = pd.DataFrame(data["teams"])
        dataframe = dataframe[["code", "id", "name", "strength_overall_home", "strength_overall_away", "strength_attack_home", "strength_attack_away", "strength_defence_home", "strength_defence_away"]]
        return dataframe

    def getUserData(user):
        '''Downloads user data, returns a dictionary'''
        file = open("key.key", "rb")
        key = file.read()
        file.close()
        f = Fernet(key)

        session = requests.session()
        url = "https://users.premierleague.com/accounts/login/"

        headers = {
            "authority": "users.premierleague.com" ,
            "cache-control": "max-age=0" ,
            "upgrade-insecure-requests": "1" ,
            "origin": "https://fantasy.premierleague.com" ,
            "content-type": "application/x-www-form-urlencoded" ,
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36" ,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9" ,
            "sec-fetch-site": "same-site" ,
            "sec-fetch-mode": "navigate" ,
            "sec-fetch-user": "?1" ,
            "sec-fetch-dest": "document" ,
            "referer": "https://fantasy.premierleague.com/my-team" ,
            "accept-language": "en-US,en;q=0.9,he;q=0.8" ,
            }

        file = open("config\\"+user+".cnfg", "rb")
        data = file.read()
        data = f.decrypt(data).decode("utf-8")
        file.close()
        data = ast.literal_eval(data)
        password = data.get("password")
        email = data.get("username")
        id = data.get("manager_id")

        payload = {
         "password": password,
         "login": email,
         "redirect_uri": "https://fantasy.premierleague.com/a/login",
         "app": "plfpl-web"
        }
    
        session.post(url, data=payload, headers=headers)
        response = session.get("https://fantasy.premierleague.com/api/my-team/"+id+"/")
        response = json.loads(response.content)
        print(response)
        userteam = response["picks"]
        userteam = pd.DataFrame(userteam)
        refinedteam = userteam[["element", "position", "is_captain", "is_vice_captain"]]
        teamdict = refinedteam.to_dict()
        return teamdict
    
def getCurrentGameweek(gameweeks):
    '''Calculates the current gameweek, takes array, returns int'''
    for i in range(len(gameweeks.index)):
        if gameweeks.iloc[i, 4] == False:
            return i+1
    
class PlayerDownloader():
    def __init__(self, playerid, currentgameweek):
        self.id = playerid
        self.totalgames = currentgameweek

    def getPlayerData(self):
        r = requests.get("https://fantasy.premierleague.com/api/element-summary/"+str(self.id)+"/")
        data = json.loads(r.content)
        dataframe = pd.json_normalize(data["history"])
        self.playerhistory = dataframe[["element", "total_points", "goals_scored", "assists", "minutes", "saves", "clean_sheets", "ict_index", "influence", "creativity", "threat", "round"]]
        self.playerhistory = self.playerhistory.rename({"total_points": "points_per_game"}, axis=1)

        r = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
        data = json.loads(r.content)
        playersframe = pd.DataFrame(data["elements"])
        self.playersubframe = playersframe[["first_name", "second_name", "code", "team", "id", "total_points", "goals_scored", "assists", "minutes", "points_per_game", "saves", "clean_sheets", "ict_index", "influence", "creativity", "threat", "element_type"]]
        self.playersubframe = self.playersubframe.sort_values("id")
        self.playerinfo = self.playersubframe.iloc[int(self.id)-1]
        self.playerteam = self.playerinfo["team"]

        return self.playerinfo, self.playerhistory 

    def calculatePlayTime(self):
        totaltime = self.playerinfo["minutes"]
        return totaltime/self.totalgames