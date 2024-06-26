import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
#from test_data_loading import LoadDataFromYF


class ZigZagIndicator:
    """Summary:
    Class for calculating and plotting the ZigZag indicator.

    Explanation:
    This class provides static methods to calculate ZigZag indicator peaks and valleys based on the provided data and a specified percentage change threshold, and to plot the ZigZag indicator with horizontal segments connecting the points.

    Args:
    - data: The input data containing High and Low prices.
    - percent_change: The threshold percentage change to filter peaks and valleys.

    Returns:
    - For calculate_zigzag: DataFrame with date, ZigZag values, and type (high or low) for the detected peaks and valleys.
    - For plot_zigzag: None
    """
    
    
    @staticmethod
    def calculate_zigzag(data, percent_change):
        """Summary:
        Calculate ZigZag indicator peaks and valleys.

        Explanation:
        This static method calculates the ZigZag indicator peaks and valleys based on the provided data and a specified percentage change threshold.

        Args:
        - data: The input data containing High and Low prices.
        - percent_change: The threshold percentage change to filter peaks and valleys.

        Returns:
        - DataFrame with date, ZigZag values, and type (high or low) for the detected peaks and valleys.
        """
        # sourcery skip: inline-immediately-returned-variable
        data_x = data.index.values
        data_high = data["High"].values
        data_low = data["Low"].values
        # Находим пики и впадины
        peak_indexes = signal.argrelextrema(data_high, np.greater)[0]
        valley_indexes = signal.argrelextrema(data_low, np.less)[0]
        # Создаем датафреймы для пиков и впадин
        data_peaks = pd.DataFrame({"date": data_x[peak_indexes], "zigzag_y": data_high[peak_indexes], "type": "high"})
        data_valleys = pd.DataFrame({"date": data_x[valley_indexes], "zigzag_y": data_low[valley_indexes], "type": "low"})
        data_peaks_valleys = pd.concat([data_peaks, data_valleys], ignore_index=True, sort=True)
        data_peaks_valleys = data_peaks_valleys.sort_values(by=["date"])
        # Удаляем лишние пики и впадины, которые не чередуются
        mask = [True]
        previous_type = data_peaks_valleys.iloc[0]["type"]
        for i in range(1, len(data_peaks_valleys)):
            current_type = data_peaks_valleys.iloc[i]["type"]
            if current_type != previous_type:
                previous_type = current_type
                mask.append(True)
            else:
                mask.append(False)
        data_peaks_valleys = data_peaks_valleys[mask]
        # Фильтруем датафрейм по порогу изменения цены
        previous_price = data_peaks_valleys.iloc[0]["zigzag_y"]
        mask = [True]
        for i in range(1, len(data_peaks_valleys)):
            current_price = data_peaks_valleys.iloc[i]["zigzag_y"]
            current_type = data_peaks_valleys.iloc[i]["type"]
            relative_difference = np.abs(current_price - previous_price) / previous_price
            if relative_difference > percent_change:
                previous_price = current_price
                mask.append(True)
            else:
                mask.append(False)
        data_peaks_valleys = data_peaks_valleys[mask]
        return (data_peaks_valleys)
    

    @staticmethod
    def plot_zigzag(data_peaks_valleys):
        """Summary:
        Plot the ZigZag indicator.

        Explanation:
        This static method generates a plot of the ZigZag indicator based on the peaks and valleys data provided.

        Args:
        - data_peaks_valleys: DataFrame containing date and ZigZag values for peaks and valleys.

        Returns:
        None
        """
        plt.figure(figsize=(10, 10))
        plt.plot(data_peaks_valleys["date"], data_peaks_valleys["zigzag_y"], color="blue", label="ZigZag")

        # Добавляем горизонтальные отрезки для каждой точки ZigZag
        for i in range(len(data_peaks_valleys) - 1):
            plt.hlines(y=data_peaks_valleys.iloc[i]["zigzag_y"], xmin=data_peaks_valleys.iloc[i]["date"], xmax=data_peaks_valleys.iloc[i + 1]["date"], color="green", linestyle=":", linewidth=1)

        plt.legend()
        plt.title('ZigZag Indicator')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.show()

""""
#Пример использования
data = LoadDataFromYF.load_test_data("AAPL", start="2022-06-14", end="2024-02-14", timeframe="1h")
print(data)
data_peaks_valleys = ZigZagIndicator.calculate_zigzag(data, percent_change=0.036098)
ZigZagIndicator.plot_zigzag(data_peaks_valleys)
"""