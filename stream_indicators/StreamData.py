import pandas as pd

from LoadDataSimulator import LoadDataSimulator


class StreamData:
    dataframe: pd.DataFrame

    def __init__(self, dataframe):
        self.dataframe = dataframe.copy()


    def get_data(self) -> pd.DataFrame:
        return self.dataframe

    def update_data(self, new_bar):
        self.dataframe.drop(index=self.dataframe.index[0], axis=0, inplace=True)
        self.dataframe = self.dataframe._append(new_bar)
