import pandas as pd
import json
import numpy as np

file = open("data\\bootstrap-static.json", "rb")
data = file.read()
file.close()
datalist = json.loads(data)
elements = datalist["elements"]

dataframe = pd.DataFrame.from_dict(elements)
#newdataframe = dataframe[["element_type", "points_per_game"]].astype({"points_per_game": "float"})
#nonzeroframe = newdataframe[newdataframe["points_per_game"] != 0.0]
#dataframegk = nonzeroframe[nonzeroframe["element_type"] == 1]
#print(dataframegk.mean())
#dataframedef = nonzeroframe[nonzeroframe["element_type"] == 2]
#print(dataframedef.mean())
#dataframemid = nonzeroframe[nonzeroframe["element_type"] == 3]
#print(dataframemid.mean())
#dataframeatk = nonzeroframe[nonzeroframe["element_type"] == 4]
#print(dataframeatk.mean())