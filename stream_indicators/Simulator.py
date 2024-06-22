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
bollinger_len = 5
bollinger_stdev = 2
stream_data_loader = StreamData(loader.get_data_in_range(upper_border=bollinger_len))
data = loader.get_data().copy()
etalon_data = loader.get_data().copy()
var = pd.DataFrame()
offset = 0

print(etalon_data.equals(data))

while var is not None:

    upper_band, middle_band, lower_band = StreamCalculator.calc_static_bbands(stream_data_loader.get_data(), bollinger_len, bollinger_stdev)
    data.at[stream_data_loader.get_data().index[-1], 'Upper Band'] = upper_band.iloc[0]
    data.at[stream_data_loader.get_data().index[-1], 'Middle Band'] = middle_band.iloc[0]
    data.at[stream_data_loader.get_data().index[-1], 'Lower Band'] = lower_band.iloc[0]

    var = loader.get_data_by_str(bollinger_len + offset)
    offset = offset + 1
    if var is None:
        break
    stream_data_loader.update_data(var)


etalon_data = BollindgerBands.calculate_bands(etalon_data, 5, 2)
print(data.equals(etalon_data))


