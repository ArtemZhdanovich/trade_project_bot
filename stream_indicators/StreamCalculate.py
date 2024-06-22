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

        #print(upper_band.tail(1))
        return upper_band.tail(1), middle_band.tail(1), lower_band.tail(1)



loadData = LoadDataSimulator()

# сигнал выход за границу и возврат