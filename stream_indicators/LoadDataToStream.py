import pandas as pd
import yfinance as yf


class LoadDataToStream:
    dataframe: pd.DataFrame

    def __init__(self):
        self.__load_static_data("AAPL", start="2023-06-14", end="2024-02-14", timeframe="1h")

    def __load_static_data(self, ticker, start, end, timeframe):
        self.dataframe = yf.download(ticker, start, end, interval=timeframe)

    def get_data(self) -> pd.DataFrame:
        return self.dataframe

    def get_data_by_str(self, iter_index=0) -> pd.DataFrame | None:
        if iter_index < len(self.dataframe):
            return self.dataframe.iloc[iter_index]
        else:
            return None

    def get_data_in_period(self, period) -> pd.DataFrame:
        data_period = pd.DataFrame(columns=self.dataframe.columns)
        i = 0
        while i < period:
            data_period = data_period._append(self.get_data_by_str(i))
            i = i + 1

        return data_period