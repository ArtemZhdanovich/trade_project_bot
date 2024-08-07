import logging
from typing import Optional
from sqlalchemy.orm import sessionmaker
import pandas as pd, datetime
from datasets.database import DataAllDatasets
from User.TradeRequests import OKXTradeRequests
from User.UserInfoFunctions import UserInfo
from utils.RiskManagment import RiskManadgment
from utils.DataFrameUtils import create_dataframe, prepare_data_to_dataframe

# !!!Важно, если не вязать IP адрес к ключу, у которого есть разрешения на вывод и торговлю(отдельно), то он автоматически удалиться через 14 дней.
#flag = "1"  live trading: 0, demo trading: 1
#instType = 'SWAP'


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('trade_functions.log')
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class PlaceOrders(OKXTradeRequests, RiskManadgment, UserInfo, DataAllDatasets):    
    def __init__(
            self, Session:sessionmaker,
            instId:Optional[str]=None, posSide:Optional[str]=None, tpPrice:Optional[float]=None,
            slPrice=None|float
            ):
        super(OKXTradeRequests).__init__(instId=instId, posSide=posSide, slPrice=slPrice, tpPrice=tpPrice)
        super(UserInfo).__init__(instId=instId)
        super(RiskManadgment).__init__(instId=instId, slPrice=slPrice)
        super(DataAllDatasets).__init__(Session)
        self.instid = instId
        self.Session = Session
        self.posSide = posSide
        self.tpPrice = tpPrice
        self.slPrice = slPrice


    # Создание маркет ордера long с Tp и Sl
    def place_market_order(self) -> str:
        try:
            result = {
                'instID':  self.instId,
                'timeframe': self.timeframe,
                'leverage': super().set_leverage_inst(),
                'posSide': self.posSide,
                'tpPrice': self.tpPrice,
                'slPrice': self.slPrice,
                'posFlag': True
            }
            self.balance, result['balance'] = super().check_balance()
            contract_price, result['contract_price'] = super().check_contract_price_cache(self.instId)
            self.size, result['size'] = super().calculate_pos_size(contract_price)
            result |= super().construct_market_order()
            if result['order_id'] is not None:
                result['enter_price'] = super().check_position(result['order_id'])
                if self.tpPrice is None:
                    result['order_id_tp'] = None
                else:
                    result['order_id_tp'] = super().construct_takeprofit_order()
                if self.slPrice is None:
                    result['order_id_sl'] = None
                else:
                    result['order_id_sl'] = super().construct_stoploss_order()
                super().save_new_order_data(result)
            else:
                print("Unsuccessful order request, error_code = ",result["data"][0], ", Error_message = ", result["data"][0]["sMsg"])
            return result['order_id']
        except Exception as e:
            logger.error(f"\n{datetime.datetime.now().isoformat()} Error place market order:\n{e}")
        
        
    # Размещение лимитного ордера
    def place_limit_order(self, price:float) -> str:
        try:
            result = {
                'instID':  self.instId,
                'timeframe': self.timeframe,
                'leverage': super().set_leverage_inst(),
                'posSide': self.posSide,
                'tpPrice': self.tpPrice,
                'slPrice': self.slPrice,
                'enter_price': price,
                'posFlag': False,
            }
            self.balance, result['balance'] = super().check_balance()
            contract_price, result['contract_price'] = super().check_contract_price_cache(self.instId)
            self.size, result['size'] = super().calculate_pos_size(contract_price)
            # limit order
            result, order_id, outTime = super().construct_limit_order(price)
            if self.tpPrice is None:
                result['order_id_tp'] = None
            else:
                result['order_id_tp'] = super().construct_takeprofit_order()
            if self.slPrice is None:
                result['order_id_sl'] = None
            else:
                result['order_id_tp'] = super().construct_takeprofit_order()
            if order_id is not None:
                super().save_new_order_data(result)
            else:
                print("Unsuccessful order request, error_code = ",result["data"][0]["sCode"], ", Error_message = ", result["data"][0]["sMsg"])
            return order_id
        except Exception as e:
            logger.error(f"\n{datetime.datetime.now().isoformat()} Error place limit order:\n{e}")


    def get_current_chart_data(self) -> pd.DataFrame:
        try:
            result = super().get_market_data()
            if 'data' in result and len(result["data"]) > 0:
                data_list = prepare_data_to_dataframe(result)
                return create_dataframe(data_list)
            else:
                print("Данные отсутствуют или неполные")
        except Exception as e:
            logger.error(f" \n{datetime.datetime.now().isoformat()} Error get current chart data:\n{e}")