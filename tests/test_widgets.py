import sys
sys.path.append('..')
from main import UserTeamWidget
from summary_page import pandasModel
import json
import pandas as pd

def test_createPlayerLists():
    dataframe = getTestData()
    assert (UserTeamWidget.createNamesList(1, False, dataframe, None) == ["Aaron Ramsdale"])

def test_pandasModel():
    dataframe = getTestData()
    pandastable = pandasModel(dataframe)
    assert (pandastable.rowCount() == 4)
    assert (pandastable.columnCount() == 27)

def getTestData():
    file = open("test_data.json", "r")
    data = file.read()
    file.close()
    data = json.loads(data)
    dataframe = pd.DataFrame(data)
    return dataframe