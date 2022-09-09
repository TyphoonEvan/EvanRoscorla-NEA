import requests
import json
import pandas as pd

#def getData():
#    config = open("config.json", "r")
#    configlist = config.read()
#    config.close()
#    configlist = json.loads(configlist)
#    for i in range(len(configlist)):
#        currentitem = configlist[i]
#        try:
#            response = requests.get(currentitem.get("url"), allow_redirects=True)
#            response.raise_for_status()
#        except requests.exceptions.HTTPError as e:
#            raise SystemExit(e)
#        filename = 'data\\' + currentitem.get("name") + '.json'
#        f = open(filename, "wb")
#        f.write(response.content)
#        f.close()
#
#def getUserData(username):
#    config = open("config.json", "r")
#    configlist = config.read()
#    config.close()
#    configlist = json.loads(configlist)
#    line = configlist[4]
#    url = line.get("url")
#    users_config = open("users_config.json", "r")
#    users_configlist = users_config.read()
#    users_config.close()
#    users_configlist = json.loads(users_configlist)
#    num = [i for i, d in enumerate(users_configlist) if username in d.values()]
#    num = num[0]
#    id = users_configlist[num].get("manager_id")
#    replacedurl = url.replace("{manager_id}", str(id))
#    config = open("config.json", "r")
#    configlist = config.read()
#    config.close()
#    configlist = json.loads(configlist)
#    try:
#        response = requests.get(replacedurl, allow_redirects=True)
#        response.raise_for_status()
#    except requests.exceptions.HTTPError as e:
#        raise SystemExit(e)
#    filename = 'data\\' + line.get("name") + '.json'
#    f = open(filename, "wb")
#    f.write(response.content)
#    f.close()

class DataReader():
    def getGenericData(self):
        pass

    def getUserData(user):
        config = open("config.json", "r")
        configlist = config.read()
        config.close()
        configlist = json.loads(configlist)
        urls = []
        for i in range(len(configlist)):
            if "{manager_id}" in configlist[i].get("url"):
                urls.append(configlist[i])
        for i in range(len(urls)):
            currentitem = urls[i]
            try:
                url = currentitem.get("url")
                url = url.replace("{manager_id}", user.get("manager_id"))
                response = requests.get(url, allow_redirects=True)
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise SystemExit(e)
            filename = 'data\\' + currentitem.get("name") + "-" + user.get("name") + '.json'
            f = open(filename, "wb")
            f.write(response.content)
            f.close()

def downloadToDataFrame(url):
    dataframe = pd.read_json(url)
    dataframe.head

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