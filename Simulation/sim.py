import pandas as pd
from api.okx_info import OKXInfoFunctions
from datasets.database import DataAllDatasets
from datasets.utils.dataframe_utils import generate_time_points, prepare_many_data_to_append_db


bd = DataAllDatasets('ETH-USDT-SWAP', '4H')
get = OKXInfoFunctions('ETH-USDT-SWAP', '4H')
dates = generate_time_points(20)
for date in dates:
    print(date)
    result = get.get_market_data(None, '1637715600', '1642006300')
    print(result)
    result = prepare_many_data_to_append_db(result)
    bd.save_charts(result)
data = bd.get_all_bd_marketdata()
print(data)
df = pd.DataFrame(data)
df.set_index('Date', inplace=True)
print(df)
