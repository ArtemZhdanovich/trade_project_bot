import pandas as pd
import talib

from LoadDataToStream import LoadDataToStream
from indicators.BollingerBands import BollindgerBands


class StreamCalculator:

    @staticmethod
    def calc_static_bbands(data, lenghts, stdev):
        # Рассчитываем среднее значение между максимальной и минимальной ценой для каждого периода
        high_low_average = (data['High'] + data['Low']) / 2
        # Рассчитываем полосы Боллинджера на основе среднего значения между High и Low
        upper_band, middle_band, lower_band = talib.BBANDS(
            high_low_average,
            timeperiod=lenghts,  # Defolt 20
            nbdevup=stdev,  # cтандарт 2
            nbdevdn=stdev,  # стандарт 2 не знаю нахуя тут два пункта
            matype=0  # тип скользящей
        )

        return upper_band.tail(1), middle_band.tail(1), lower_band.tail(1)

    @staticmethod
    def calc_stream_bbands(loadData, lenghts, stdev) -> pd.DataFrame:
        data_to_calculate = loadData.get_data_in_period(lenghts+1)
        var = 0
        offset = 0
        ret_data = pd.DataFrame()
        while var is not None:
            var = loadData.get_data_by_str(lenghts + offset)
            offset = offset + 1
            if var is None:
                break
            data_to_calculate.drop(index=data_to_calculate.index[0], axis=0, inplace=True)
            data_to_calculate = pd.concat([data_to_calculate, var])
            upper_band, middle_band, lower_band = StreamCalculator.calc_static_bbands(data_to_calculate, lenghts, stdev)

        return ret_data


loadData = LoadDataToStream()
#BollindgerBands.create_vizualization_bb(StreamCalculator.calc_static_bbands(loadData.get_data(), 34, 2))
#BollindgerBands.create_vizualization_bb(loadData.get_data(), StreamCalculator.calc_stream_bbands(loadData, 34, 2))
up, mid, low = StreamCalculator.calc_static_bbands(loadData.get_data_in_period(30), 30, 2)
#print(f"date: {datetime},\n up:{up},\n mid:{mid},\n low:{low}\n")
#print(res)
data = loadData.get_data_in_period(30)
data['Upper band'] = up
data['Middle band'] = mid
data['Lower band'] = low
print(data)
#print(StreamCalculator.calc_stream_bbands(loadData, 34,2))

