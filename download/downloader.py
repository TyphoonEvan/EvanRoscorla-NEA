import requests
import json

def getData():
    config = open("config.json", "r")
    configlist = config.read()
    config.close()
    configlist = json.loads(configlist)
    for i in range(len(configlist)):
        currentitem = configlist[i]
        try:
            response = requests.get(currentitem.get("url"), allow_redirects=True)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise SystemExit(e)
        filename = 'data\\' + currentitem.get("name") + '.json'
        f = open(filename, "wb")
        f.write(response.content)
        f.close()

def getUserData(username):
    config = open("config.json", "r")
    configlist = config.read()
    config.close()
    configlist = json.loads(configlist)
    line = configlist[4]
    url = line.get("url")
    users_config = open("users_config.json", "r")
    users_configlist = users_config.read()
    users_config.close()
    users_configlist = json.loads(users_configlist)
    num = [i for i, d in enumerate(users_configlist) if username in d.values()]
    num = num[0]
    id = users_configlist[num].get("manager_id")
    replacedurl = url.replace("{manager_id}", str(id))
    config = open("config.json", "r")
    configlist = config.read()
    config.close()
    configlist = json.loads(configlist)
    try:
        response = requests.get(replacedurl, allow_redirects=True)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise SystemExit(e)
    filename = 'data\\' + line.get("name") + '.json'
    f = open(filename, "wb")
    f.write(response.content)
    f.close()