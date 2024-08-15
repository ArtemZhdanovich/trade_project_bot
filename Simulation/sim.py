import sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
import pandas as pd, okx.MarketData as MarketData
from api.okx_info import OKXInfoFunctions
from datasets.database import DataAllDatasets
from datasets.utils.dataframe_utils import prepare_many_data_to_append_db, generate_time_points
from configs.load_settings import LoadUserSettingData

api_settings = LoadUserSettingData().load_api_setings()
flag = api_settings['flag']
marketDataAPI = MarketData.MarketAPI(flag=flag)


bd = DataAllDatasets('ETH-USDT-SWAP', '4H')
get = OKXInfoFunctions('ETH-USDT-SWAP', '4H')
dates = generate_time_points(5)
for date in dates:
    result = marketDataAPI.get_candlesticks('ETH-USDT-SWAP', f'{date}', None, '4H', 100 )
    data = prepare_many_data_to_append_db(result)
    bd.save_charts(data)
r = bd.get_all_bd_marketdata()
df = pd.DataFrame(r)
df.set_index('Date', inplace=True)
print(df)
