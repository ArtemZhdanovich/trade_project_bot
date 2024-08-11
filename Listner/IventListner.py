#libs
import contextlib, time
from typing import Optional
#database
from DataSets.StatesDB import StateRequest
from DataSets.AsyncStatesDB import AsyncStateRequest
#cache
from Cache.RedisCache import RedisCache
from Cache.AioRedisCache import AioRedisCache
#functions
from Api.OKXTradeFunctions import PlaceOrders
from Api.OKXInfoAsync import OKXInfoFunctionsAsync
#utils
from BaseLogs.CustomLogger import create_logger
logger = create_logger('IventListner')





class OKXIventListner(RedisCache, AioRedisCache):
    def __init__(self, orderId:Optional[str]=None):
        RedisCache.__init__(key='positions')
        AioRedisCache.__init__(key='positions')
        self.orderId = orderId


    def __find_index(self, positions:dict) -> int:
        instIds_match_list = [i for i, val in enumerate(positions['instId']) if val == self.instId]
        for index in instIds_match_list:
            element_b = positions['timeframe'][index]
            is_match = element_b == self.timeframe
            if is_match:
                search_index = index
                break
        return search_index


    def __update_pos_if(self, positions:dict, message:dict):
        try:
            search_index = self.__find_index(positions)
            positions['state'][search_index], positions['orderId'][search_index] = message['state'], self.orderId
            positions['strategy'][search_index], positions['status'][search_index] = message['strategy'], True
            StateRequest(self.instId, self.timeframe, self.strategy).update_state(positions)
            return positions
        except ValueError:
            message['orderId'] = self.orderId
            positions |= message
            StateRequest(self.instId, self.timeframe).save_position_state(positions)
            return positions


    def __update_pos_else(self, message:dict):
        message['orderId'] = self.orderId
        message = {key: [value] for key, value in message.items()}
        positions = message
        StateRequest(self.instId, self.timeframe).save_position_state(positions)
        return positions


    def create_listner(self):
        self.subscribe_to_redis_channels()
        while True:
            try:
                with contextlib.suppress(Exception):
                    message = self.check_redis_message()
                    self.instId, self.timeframe, self.strategy  = message['instId'], message['timeframe'], message['strategy']
                    self.orderId = PlaceOrders(message['instId'], None, message['signal'],\
                        None, message['slPrice']).place_market_order()
                    if positions := self.load_message_from_cache():
                        positions = self.__update_pos_if(positions, message)
                    else:
                        positions = self.__update_pos_else(message)
                    self.send_redis_command(positions, self.key)
                time.sleep(10)
            except Exception as e:
                logger.error(f'Error:{e}')


    async def ivent_reaction(self, msg:dict) -> None:
        try:
            if msg['data'][0]:
                data = {'orderId': msg['data'][0]['posId'], 'pos': msg['data'][0]['pos'],
                        'instId': msg['data'][0]['instId']}
                if data['pos'] == '0':
                    positions = await self.async_load_message_from_cache()
                    search_index = await self.__find_index_async(positions)
                    await self.__add_db_close_data(data, search_index)
        except Exception as e:
            logger.error(f'Error:{e}')


    async def __add_db_close_data(self, data:dict, search_index:int) -> None:
        self.instId, self.timeframe  = data['instId'][search_index], data['timeframe'][search_index]
        data['orderId'][search_index] = None
        data['priceClose'][search_index] = await OKXInfoFunctionsAsync().get_last_price(self.instId)
        await self.async_send_redis_command()
        await AsyncStateRequest(self.instId, self.timeframe).save_position_state_async(data)


    async def __find_index_async(self, positions:dict) -> int:
        instIds_match_list = [i for i, val in enumerate(positions['instId']) if val == self.instId]
        for index in instIds_match_list:
            element_b = positions['timeframe'][index]
            is_match = element_b == self.timeframe
            if is_match:
                search_index = index
                break
        return search_index
