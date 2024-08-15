import sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
import pandas as pd
from api.okx_info import OKXInfoFunctions
from datasets.database import DataAllDatasets
from datasets.utils.dataframe_utils import prepare_many_data_to_append_db, generate_time_points, create_timestamp


import okx.MarketData as MarketData
marketApi = MarketData.MarketAPI(flag = '1') #Demo
dates = generate_time_points(22) #return list of Timestamps, format '14994040312' str
timestamps =[]
for timestamp in dates:
    x = create_timestamp(timestamp)
    timestamps.append(x)
print(dates[2] == dates[21]) #returns False
print(dates)
a = marketApi.get_history_candlesticks('ETH-USDT', timestamps[0], timestamps[10], '1H', ' ')
print(a)
b = marketApi.get_history_candlesticks('ETH-USDT', timestamps[0], timestamps[10], '1H', ' ')
print(b)
print(a==b) #returns True
"""
data = prepare_many_data_to_append_db(result)
bd.save_charts(data)
r = bd.get_all_bd_marketdata()
df = pd.DataFrame(r)
df.set_index('Date', inplace=True)
print(df)
"""
