import sys
sys.path.append('..')
from download.downloader import getCurrentGameweek, PlayerDownloader
import json
import pandas as pd

def test_getGameweek():
    file = open("test_gameweek.json", "r")
    data = file.read()
    file.close()
    data = json.loads(data)
    gameweeks = pd.DataFrame(data)
    assert (getCurrentGameweek(gameweeks) == 24)

def test_calculatePlayTime():
    playerdownloader = PlayerDownloader(318, 24)
    with open("bootstrap-static.json", "rb") as file:
        data = file.read()
        file.close()
    data = json.loads(data)
    playersframe = pd.DataFrame(data["elements"])
    playersubframe = playersframe[["first_name", "second_name", "code", "team", "id", "total_points", "goals_scored", "assists", "minutes", "points_per_game", "saves", "clean_sheets", "ict_index", "influence", "creativity", "threat", "element_type"]]
    playersubframe = playersubframe.sort_values("id")
    playerinfo = playersubframe.iloc[318]
    assert (playerdownloader.calculatePlayTime(playerinfo, 24) == 25.541666666666668)