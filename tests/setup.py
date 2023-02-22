import sys
sys.path.append('..')
import requests
import json
import pandas as pd
from download.downloader import PlayerDownloader

playerdownloader = PlayerDownloader(318, 24)
playerinfo, playerhistory = playerdownloader.getPlayerData()
print(playerdownloader.calculatePlayTime(playerinfo, 24))