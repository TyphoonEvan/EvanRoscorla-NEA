import sys
sys.path.append('..')
from team_optimiser import PerformancePredictor
import pandas as pd
import json

def test_linearRegression():
    df = pd.DataFrame([[1,2,3,4],[5,7,9,11]])
    assert (PerformancePredictor.getPrediction(df) == 3, 2)

def test_performancePrediction():
    file = open("test_player.json", "r")
    data = file.read()
    file.close()
    data = json.loads(data)
    df = pd.DataFrame(data)
    performancePredictor = PerformancePredictor(df)
    file = open("test_table.json", "r")
    data = file.read()
    file.close()
    data = json.loads(data)
    dataframe = pd.DataFrame(data)
    table = performancePredictor.predictPerformance()
    assert (not table.empty)
    assert (not table.compare(dataframe).empty)