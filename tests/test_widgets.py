import sys
sys.path.append('..')
from user_team import UserTeamWidget
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

def test_MostRecentFile():
    with open("test_files\\file1.txt", "w") as file:
        file.write("1")
        file.close()
    filename = UserTeamWidget.GetLastModified("test_files")
    with open(filename, "r") as file:
        assert (file.read() == "1")
        file.close()