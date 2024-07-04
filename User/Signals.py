import sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
import logging
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from User.LoadSettings import LoadUserSettingData
from datasets.LoadDataStream import StreamData
from indicators.AVSL import AVSLIndicator
from indicators.ADX import ADXTrend
from indicators.RsiClouds import CloudsRsi
from datasets.RedisCache import RedisCache
from datasets.StatesDB import SQLStateStorage, StateRequest
from datasets.database import Session
from utils.DataFrameUtils import create_message_state


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('signals.log')
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class CheckSignalData(LoadUserSettingData):
    def __init__ (self, Session:sessionmaker, classes_dict:dict, instId:str, timeframe:str, lenghtsSt:int):
        super().__init__()
        self.lenghtsSt = lenghtsSt
        self.instId = instId
        self.timeframe = timeframe
        self.Session = Session
        self.classes_dict = classes_dict
        self.channel = f'channel_{self.instId}_{self.timeframe}'
        self.init = StreamData(self.Session, self.classes_dict, self.instId, self.timeframe, self.lenghtsSt)
        data = self.init.load_data()
        self.redis_func = RedisCache(self.instId, self.timeframe, self.channel, data)
        self.redis_func.add_data_to_cache(data)


    def create_signals(self) -> None:
        try:
            data = self.redis_func.load_data_from_cache()
            data = self.init.load_data_for_period(data)
            indicator_avsl = AVSLIndicator(data)
            indicator_rsi_clouds = CloudsRsi(data)
            indicator_adx = ADXTrend(data)
            avsl = indicator_avsl.calculate_avsl()
            rsi = indicator_rsi_clouds.calculate_rsi_clouds()
            adx = indicator_adx.calculate_adx()
            message = create_message_state(self.instId, self.timeframe, avsl, adx, rsi)
            self.redis_func.add_data_to_cache(data)
            if rsi is not None and adx >= self.adx_tigger:
                self.redis_func.publish_message(self.channel, message)
        except Exception as e:
            logger.error(f"\n{datetime.datetime.now().isoformat()} Error create signals:\n{e}")


    def trailing_stoploss(self) -> None: #Базирован на индикаторе авсл
        try:
            data = self.redis_func.load_data_from_cache()
            data = self.init.load_data_for_period(data)
            indicator_avsl = AVSLIndicator(data)
            avsl = indicator_avsl.calculate_avsl()
            # Добавить метод для изменения стопа!!!
        except Exception as e:
            logger.error(f"\n{datetime.datetime.now().isoformat()} Error trailing stoploss:\n{e}")
            

"""
#Это надо встроить в маин            
engine = create_engine("sqlite:///./datasets/TradeUserDatasets.db")
data_all_datasets = DataAllDatasets()
classes_dict = data_all_datasets.create_classes(Base)   
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)   
signal = CheckSignalData(Session, classes_dict, 'ETH-USDT-SWAP', '4H', 300, 'my_channel')
signal.avsl_signals()
"""
