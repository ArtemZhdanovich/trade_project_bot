#libs
import sys, asyncio
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from typing import Optional
from sqlalchemy.sql import exists
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
#database
from datasets.tables import Base, ClassCreation, PositionAndOrders
#utils
from baselogs.custom_decorators import log_exceptions_async, retry_on_exception_async
from baselogs.custom_logger import create_logger


logger = create_logger(logger_name='DataBaseAsync')


class DataAllDatasetsAsync:
    async def __init__(self, instId:Optional[str]=None, timeframe:Optional[str]=None):
        self.instId = instId
        self.timeframe = timeframe
        await self.__create_tables_async()

    async def __create_tables_async(self):
        engine2 = create_async_engine("sqlite+aiosqlite:///./datasets/TradeUserDatasets.db")
        self.AsyncSessionLocal = sessionmaker(bind=engine2, class_=AsyncSession)
        self.classes_dict = ClassCreation().create_classes(Base)
        async with engine2.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


    @event.listens_for(PositionAndOrders, 'after_insert')
    async def calculate_money_income(self, mapper, connection, target):
        async with self.AsyncSessionLocal() as session:
            try:
                target.MONEY_INCOME = (target.ENTER_PRICE - target.CLOSE_PRICE) * target.LEVERAGE - target.FEE
            except Exception as e:
                await session.rollback()
                raise e


    @event.listens_for(PositionAndOrders, 'after_insert')
    async def calculate_percent_money_income(self, mapper, connection, target):
        async with self.AsyncSessionLocal() as session:
            try:
                target.PERCENT_MONEY_INCOME = (target.MONEY_INCOME / target.BALANCE) * 100
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e


    @event.listens_for(PositionAndOrders, 'after_insert')
    async def calculate_money_in_deal(self, mapper, connection, target):
        async with self.AsyncSessionLocal() as session:
            try:
                target.MONEY_IN_DEAL = target.BALANCE * target.RISK_COEFFICIENT + target.FEE
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e


    @retry_on_exception_async(logger)
    async def __process_data_get_all_bd_marketdata_async(self, session:AsyncSession, table):
        columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume', 'Volume Usdt']
        query = await session.query(
                    table.c.TIMESTAMP, table.c.OPEN, table.c.CLOSE, table.c.HIGH,
                    table.c.LOW, table.c.VOLUME, table.c.VOLUME_USDT
                ).order_by(table.c.TIMESTAMP).all()
        return {col: [row[i] for row in query] for i, col in enumerate(columns)}


    async def get_all_bd_marketdata_async(self) -> dict:
        class_ = self.classes_dict[f"{self.instId}_{self.timeframe}"]
        table = class_.__table__
        async with self.AsyncSessionLocal() as session:
            return await self.__process_data_get_all_bd_marketdata_async(session, table)


    @log_exceptions_async(logger)
    async def __process_data_save_charts_async(self, i, results_dict, session, active_class):
        target_data = await session.execute(select(exists().where(active_class.TIMESTAMP == results_dict['Date'][i])))
        target_data = target_data.scalar()
        if not target_data:
            data = active_class(
                TIMESTAMP=results_dict['Date'][i], INSTRUMENT=self.instId,
                TIMEFRAME=self.timeframe, OPEN=results_dict['Open'][i],
                CLOSE=results_dict['Close'][i], HIGH=results_dict['High'][i],
                LOW=results_dict['Low'][i], VOLUME=results_dict['Volume'][i],
                VOLUME_USDT=results_dict['Volume Usdt'][i]
            )
            await session.add(data)
            await session.commit()


    async def save_charts_async(self, results_dict: dict) -> None:
        class_name = f"{self.instId}_{self.timeframe}"
        active_class = self.classes_dict[class_name]
        async with self.AsyncSessionLocal() as session:
            tasks = [
                self.__process_data_save_charts_async(i, results_dict, session, active_class)
                for i in range(len(results_dict['Date']))
            ]
            await asyncio.gather(*tasks)


    @log_exceptions_async(logger)
    async def __process_data_add_data_to_db_async(self, active_class, results_dict:dict, session:AsyncSession) -> None:
        data = active_class(
            TIMESTAMP=results_dict['Date'], INSTRUMENT=self.instId,
            TIMEFRAME=self.timeframe, OPEN=results_dict['Open'],
            CLOSE=results_dict['Close'], HIGH=results_dict['High'],
            LOW=results_dict['Low'], VOLUME=results_dict['Volume'],
            VOLUME_USDT=results_dict['Volume Usdt']
        )
        exists_query = await session.execute(
            select(exists().where(active_class.TIMESTAMP == data.TIMESTAMP))
        )
        if not exists_query.scalar():
            await session.add(data)
            await session.commit()


    # Добавление одной строки 
    async def add_data_to_db_async(self, results_dict: dict) -> None:
        active_class = self.classes_dict[f"ChartsData_{self.instId}_{self.timeframe}"]
        async with self.AsyncSessionLocal() as session:
            await self.__process_data_add_data_to_db_async(active_class, results_dict, session)


    @log_exceptions_async(logger)
    async def __process_data_save_new_order_data_async(self, result:dict, session:AsyncSession) -> None:
        order_id = PositionAndOrders(
            order_id=result['order_id'], status=result['posFlag'],
            order_volume=result['size'], tp_order_volume=result['size'],
            sl_order_volume=result['size'], balance=result['balance'],
            instrument=result['instId'], leverage=result['leverage'],
            side_of_trade=result['posSide'], enter_price=result['enter_price'],
            time=result['outTime'], tp_order_id=result['order_id_tp'],
            tp_price=result['tpPrice'], sl_order_id=result['order_id_sl'],
            sl_price=result['slPrice']
        )
        await session.add(order_id)
        await session.commit()


    async def save_new_order_data_async(self, result:dict) -> None:
        async with self.AsyncSessionLocal() as session:
            await self.__process_data_save_new_order_data_async(result, session)