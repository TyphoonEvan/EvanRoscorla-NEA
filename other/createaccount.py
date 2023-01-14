from cryptography.fernet import Fernet
import ast
import json

# user = {"name": "Evan", "password": "Typhoon1998_", "manager_id": "8056230", "username": "evanroscorla@gmail.com"}
# user = f.encrypt(str(user).encode("utf-8"))
# filename = "config\\Evan.cnfg"
# file = open(filename, "wb")
# file.write(user)
# file.close()

teamdict = {"1": 15, "2": 313, "3": 170, "4": 280, "5": 160, "6": 301, "7": 130, "8": 19, "9": 95, "10": 210, "11": 318}
file = open("data\\Evan-Team.json", "w")
data = json.dumps(teamdict)
file.write(data)
file.close()