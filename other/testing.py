import pandas as pd
import json

file = open("player-data.json", "r")
data = file.read()
file.close()

data = json.loads(data)
dataframe = pd.DataFrame(data)
dataframe = dataframe.iloc[[2, 4, 10, 14], :]
data = dataframe.to_json()
file = open("test_data.json", "w")
file.write(data)
file.close()