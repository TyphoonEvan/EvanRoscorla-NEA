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
    playerinfo, playerhistory = playerdownloader.getPlayerData()
    assert (playerdownloader.calculatePlayTime(playerinfo, 24) == 77.5)