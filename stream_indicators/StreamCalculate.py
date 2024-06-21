import pandas as pd
import talib

from LoadDataSimulator import LoadDataSimulator
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
    def calc_stream_bbands_cycle(loadData, lenghts, stdev) -> pd.DataFrame:
        data_to_calculate = loadData.get_data_in_period(lenghts+1)
        var = 0
        offset = 0
        ret_data = pd.DataFrame()
        while var is not None:
            var = loadData.get_data_by_str(lenghts + offset)
            offset = offset + 1
            if var is None:
                break

        return ret_data

    @staticmethod
    def calc_stream_bbands(data, new_bar, lenghts, stdev):
        #data.drop(index=data.index[0], axis=0, inplace=True)
        #data = pd.concat([data, new_bar])
        upper_band, middle_band, lower_band = StreamCalculator.calc_static_bbands(data, lenghts, stdev)

        return data, upper_band, middle_band, lower_band


loadData = LoadDataSimulator()

# сигнал выход за границу и возврат