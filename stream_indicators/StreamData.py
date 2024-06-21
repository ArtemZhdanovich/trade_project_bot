import pandas as pd

from LoadDataSimulator import LoadDataSimulator


class StreamData:
    dataframe: pd.DataFrame

    def __init__(self, window_size):
        self.dataframe = LoadDataSimulator().get_data_in_range(upper_border=window_size + 2)

    def get_data(self) -> pd.DataFrame:
        return self.dataframe

    def update_data(self, new_bar):
        self.dataframe.drop(index=self.dataframe.index[0], axis=0, inplace=True)
        self.dataframe = pd.concat([self.dataframe, new_bar])
