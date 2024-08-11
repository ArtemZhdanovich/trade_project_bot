#libs
import sys
from typing import Optional
from datetime import datetime
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
#database
from DataSets.StatesDB import StateRequest
#cache
from Cache.RedisCache import RedisCache
from Cache.LoadDataStream import StreamData
#functions
from Indicators.AVSL import AVSLIndicator
from Indicators.ADX import ADXTrend
from Indicators.RsiClouds import CloudsRsi
#utils
from BaseLogs.CustomLogger import create_logger
from BaseLogs.CustomDecorators import log_exceptions


logger = create_logger('Signals')


class CheckActiveState(StreamData, RedisCache):
    def __init__(self, instId:str, timeframe:str, lenghtsSt:int, strategy:str) -> None:
        self.lenghtsSt, self.instId, self.timeframe, self.strategy  = lenghtsSt, instId, timeframe, strategy
        self.channel = f'channel_{self.instId}_{self.timeframe}'
        StreamData.__init__(self, self.instId, self.timeframe, self.lenghtsSt, None, None)
        RedisCache.__init__(self, self.instId, self.timeframe, self.channel, key='positions')
        
    
    def __find_index(self, positions:dict) -> int:
        instIds_match_list = [i for i, val in enumerate(positions['instId']) if val == self.instId]
        for index in instIds_match_list:
            element_b = positions['timeframe'][index]
            is_match = element_b == self.timeframe
            if is_match:
                search_index = index
                break
        return search_index


    def check_active_state(self) -> Optional[dict]:
        try:
            positions = self.load_message_from_cache()
            search_index = self.__find_index(positions)
            return positions['state'][search_index]
        except Exception:
            state_instance = StateRequest(self.instId, self.timeframe, self.strategy)
            if state_params := state_instance.check_state():
                return state_params['state']
            state_instance.save_none_state()
            return None


    def add_data_to_redis(self):
        result = self.load_data()
        prepare_df = prepare_many_data_to_append_db(result)
        DataAllDatasets(self.instId, self.timeframe).save_charts(prepare_df)
        data = create_dataframe(prepare_df)
        self.add_data_to_cache(data)



class AVSL_RSI_ClOUDS(CheckActiveState):
    def __init__ (self, instId:str, timeframe:str, lenghtsSt:int) -> None:
        self.strategy = 'avsl_rsi_clouds'
        CheckActiveState.__init__(self, instId, timeframe, lenghtsSt, self.strategy)
        self.adx_trigger = 20


    def __create_signal_message(self) -> dict:
        return dict([
            ('time', datetime.now().isoformat()),
            ('instId', self.instId),
            ('timeframe', self.timeframe),
            ('strategy', self.strategy),
            ('trend_strenghts', self.adx),
            ('signal', self.rsi_clouds),
            ('slPrice', self.avsl['last'])
        ])


    @log_exceptions(logger)
    def create_signals(self) -> None:
            data = self.load_data_from_cache()
            data = self.load_data_for_period(data)
            self.avsl = AVSLIndicator(data).calculate_avsl()
            self.rsi_clouds = CloudsRsi(data).calculate_rsi_macd()
            self.adx = ADXTrend(data)._calculate_adx_sync()
            print(f'{self.avsl}\n{self.rsi_clouds}\n{self.adx}')
            message = self.__create_signal_message()
            self.add_data_to_cache(data)
            if self.rsi_clouds is not None and self.adx >= self.adx_trigger:
                self.publish_message(message)


    @log_exceptions(logger)
    def trailing_stoploss(self) -> None: #Базирован на индикаторе авсл
        data = self.load_data_from_cache()
        data = self.load_data_for_period(data)
        self.avsl = AVSLIndicator(data).calculate_avsl()
        self.adx, self.rsi_clouds = None
        message = self.__create_signal_message()
        self.publish_message(self.channel, message)
