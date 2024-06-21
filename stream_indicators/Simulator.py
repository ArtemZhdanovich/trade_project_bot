import pandas as pd

from LoadDataSimulator import LoadDataSimulator
from StreamCalculate import StreamCalculator
from StreamData import StreamData
from indicators.BollingerBands import BollindgerBands


def calc_stream_bbands_cycle(loadData, lenghts, stdev) -> pd.DataFrame:
    data_to_calculate = loadData.get_data_in_period(lenghts + 1)
    var = 0
    offset = 0
    ret_data = pd.DataFrame()
    while var is not None:
        var = loadData.get_data_by_str(lenghts + offset)
        offset = offset + 1
        if var is None:
            break

    return ret_data


#default parameters
loader = LoadDataSimulator()
bollinger_len = 30
bollinger_stdev = 2
stream_data = StreamData(bollinger_len).get_data()
data = loader.get_data()
var = pd.DataFrame()
offset = 0

while var is not None:
    var = loader.get_data_by_str(bollinger_len + offset)
    offset = offset + 1
    if var is None:
        break
    upper_band, middle_band, lower_band = StreamCalculator.calc_stream_bbands(stream_data, var, bollinger_len, bollinger_stdev)
    data['Upper band'] = upper_band
    data['Middle_band'] = middle_band
    data['Lower_band'] = lower_band
    stream_data.update_data(var)

print(data)
