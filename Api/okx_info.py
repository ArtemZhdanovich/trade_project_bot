#libs
from typing import Optional, Union
from datetime import datetime, timedelta
import okx.Account as Account, okx.MarketData as MarketData, pandas as pd, contextlib
#configs
from configs.load_settings import LoadUserSettingData
#cache
from cache.redis_cache import RedisCache
#utils
from docx import Document
from datasets.utils.dataframe_utils import validate_get_data_params
from baselogs.custom_decorators import retry_on_exception
from baselogs.custom_logger import create_logger
from baselogs.custom_logger import MultilineJSONFormatter



logger = create_logger('OKXInfo')


"""
# Данные Api
# !!!Важно, если не вязать IP адрес к ключу,
у которого есть разрешения на вывод и торговлю(отдельно),
то он автоматически удалиться через 14 дней.
"""

class OKXInfoFunctions(RedisCache):
    def __init__(
        self, instId:Optional[str]=None, timeframe:Optional[str]=None, lenghts:Optional[int]=None, 
        load_data_after:Optional[str]=None, load_data_before:Optional[str]=None
        ):
        self.key = 'contracts_prices'
        self.instId = instId
        self.timeframe = timeframe
        self.lenghts = lenghts
        self.load_data_after = load_data_after
        self.load_data_before = load_data_before
        api_settings = LoadUserSettingData().load_api_setings()
        self.api_key = api_settings['api_key']
        self.secret_key = api_settings['secret_key']
        self.passphrase = api_settings['passphrase']
        self.flag = api_settings['flag']
        user_settings = LoadUserSettingData().load_user_settings()
        self.leverage = user_settings['leverage']
        self.mgnMode = user_settings['mgnMode']
        self.risk = user_settings['risk']
        self.instIds = user_settings['instIds']
        self.timeframes = user_settings['timeframes']
        self.format = MultilineJSONFormatter()


    def __create_accountAPI(self):
        self.accountAPI = Account.AccountAPI(
            self.api_key, self.secret_key,
            self.passphrase, False, self.flag
        )


    def __create_marketAPI(self):
        self.marketDataAPI = MarketData.MarketAPI(flag=self.flag)


    def __check_result(self, result):
        if result['code'] != '0':
            raise ValueError(f'Get market data, code: {result['code']}')


    def __validate_get_data_params(
        self, history:bool, lengths:Optional[int]=None, load_data_before:Union[str, int]=None,
        load_data_after:Union[str, int]=None) -> dict:
        
        # sourcery skip: merge-else-if-into-elif
        with contextlib.suppress(Exception):
            load_data_after = self.__create_timestamp(load_data_after)
        with contextlib.suppress(Exception):
            load_data_before = self.__create_timestamp(load_data_before)
        if history:
            if isinstance(lengths, int) and lengths>100:
                raise ValueError('Lenght 100 is max')
        else:
            if isinstance(lengths, int) and lengths>300:
                raise ValueError('Lenght 100 is max')
        if isinstance(lengths, (str, type(None))):
            lengths = ' '
        limit = lengths
        before = load_data_before or ' '
        after = load_data_after or ' '
        return {'limit': limit, 'before': before, 'after': after}


    def generate_time_points(self, num_groups: int) -> list:
        #Работает только с H4, можешь модифицировать под нужные тф(5m, 15m, 1H, 1D)
        rounded_time = datetime.now().replace(minute=0, second=0, microsecond=0)
        while rounded_time.hour % 4 != 0:
            rounded_time -= timedelta(hours=1)
        time_points = []
        for _ in range(num_groups):
            time_list = [rounded_time - timedelta(hours=4 * i) for i in range(99)]
            time_points.extend(
                (
                    time_list[0].strftime('%Y-%m-%d %H:%M:%S'),
                    time_list[-2].strftime('%Y-%m-%d %H:%M:%S'),
                )
            )
            rounded_time = time_list[-2]
        return list(time_points)


    def __create_timestamp(self, time:Union[str, None]=None) -> int:
        if time is None or isinstance(time, int):
            return time
        formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d %H', '%Y-%m-%d']
        formated_time = None
        for fmt in formats:
            try:
                date_time_obj = datetime.strptime(time, fmt)
                if fmt == '%Y-%m-%d':
                    date_time_obj = date_time_obj.replace(hour=0, minute=0, second=0)
                elif fmt == '%Y-%m-%d %H':
                    date_time_obj = date_time_obj.replace(minute=0,second=0)
                formated_time = date_time_obj.strftime('%Y-%m-%d %H:%M:%S')
                break
            except ValueError:
                continue
        if not formated_time:
            raise ValueError(f"Unable to recognize date and time format: {time}")
        return int(datetime.strptime(formated_time, '%Y-%m-%d %H:%M:%S').timestamp())


    @retry_on_exception(logger)
    def get_market_data(
        self, lengths:Union[int, str, None] = None, load_data_after:Union[str, int]=None,
        load_data_before:Union[str, int]=None
        ) -> Optional[pd.DataFrame]:
        params = self.__validate_get_data_params(False, lengths, load_data_before, load_data_after)
        self.__create_marketAPI()
        result = self.marketDataAPI.get_candlesticks(
                instId=self.instId,
                after=params['after'],
                before=params['before'],
                bar=self.timeframe,
                limit=params['limit']
            )
        self.__check_result(result)
        return result


    @retry_on_exception(logger)
    def get_market_data_history(
        self, lengths:Union[int, str, None] = None, load_data_after:Optional[str]=None,
        load_data_before:Optional[str]=None
        ) -> Optional[pd.DataFrame]:
        params = self.__validate_get_data_params(True, lengths, load_data_before, load_data_after)
        self.__create_marketAPI()
        result = self.marketDataAPI.get_history_candlesticks(
                instId=self.instId,
                after=params['after'],
                before=params['before'],
                bar=self.timeframe,
                limit=params['limit']
            )
        self.__check_result(result)
        return result



    @retry_on_exception(logger)
    def check_balance(self) -> float:
        self.__create_accountAPI()
        result = self.accountAPI.get_account_balance()
        self.__check_result(result)
        return float(result["data"][0]["details"][0]["availBal"])


    # Установка левериджа кросс позиций для отдельного инструмента
    @retry_on_exception(logger)
    def set_leverage_inst(self) -> None:
        self.__create_accountAPI()
        result = self.accountAPI.set_leverage(
            instId=self.instId,
            lever=self.leverage,
            mgnMode=self.mgnMode #cross или isolated
        )
        self.__check_result(result)
        return self.leverage


    # Установка левериджа для \изолированых позиций для шорт и лонг
    @retry_on_exception(logger)
    def set_leverage_short_long(self, posSide:str) -> None:
        self.__create_accountAPI()
        result = self.accountAPI.set_leverage(
            instId = self.instId,
            lever = self.leverage,
            posSide = posSide,
            mgnMode = self.mgnMode
        )
        self.__check_result(result)


    # Установка режима торговли
    @retry_on_exception(logger)
    def set_trading_mode(self) -> None:
        self.__create_accountAPI()
        result = self.accountAPI.set_position_mode(
            posMode="long_short_mode"
        )
        self.__check_result(result)


    @retry_on_exception(logger)
    def check_contract_price(self, save:Optional[bool]=None) -> None:
        self.__create_accountAPI()
        result = self.accountAPI.get_instruments(instType="SWAP")
        self.__check_result(result)
        if save:
            doc = Document()
            doc.add_paragraph(str(result))
            doc.save('SWAPINFO.docx')
        elif save == False:
            super().send_redis_command(result, self.key)


    def check_contract_price_cache(self, instId:str) -> float:
        result = self.load_message_from_cache()
        return float(next((instrument['ctVal'] for instrument in result['data']\
            if instrument['instId'] == instId),None,))


    @retry_on_exception(logger)
    def check_instrument_price(self, instId:str) -> float:
        self.__create_marketAPI()
        result = self.marketDataAPI.get_ticker(instId)
        self.__check_result(result)
        return float(result['data'][0]['last'])