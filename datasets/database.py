#libs
import sys
sys.path.append('C://Users//Admin//Desktop//trade_project_bot')
from typing import Optional
from sqlalchemy.sql import exists
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
#database
from datasets.tables import PositionAndOrders, SQLStateStorage, classes_dict, engine
#utils
from baselogs.custom_logger import create_logger


logger = create_logger('database')
Session = sessionmaker(bind=engine)



class DataAllDatasets:
    def __init__(self, instId:Optional[str]=None, timeframe:Optional[str]=None):
        self.instId = instId
        self.timeframe = timeframe


    @event.listens_for(PositionAndOrders, 'after_insert')
    def calculate_money_in_deal(self, mapper, connection, target):
        with Session():
            target.MONEY_IN_DEAL = target.BALANCE * target.RISK_COEFFICIENT + target.FEE


    @event.listens_for(PositionAndOrders, 'after_insert')
    def calculate_money_income(self, mapper, connection, target):
        with Session():
            target.MONEY_INCOME = (target.ENTER_PRICE - target.CLOSE_PRICE) * target.LEVERAGE - target.FEE


    @event.listens_for(PositionAndOrders, 'after_insert')
    def calculate_percent_money_income(self, mapper, connection, target):
        with Session():
            target.PERCENT_MONEY_INCOME = (target.MONEY_INCOME / target.BALANCE) * 100


    def get_all_bd_marketdata(self) -> dict:
        table = classes_dict[f'{self.instId}_{self.timeframe}'].__table__
        with Session() as session:
            query = session.query(
                table.c.TIMESTAMP, table.c.OPEN, table.c.CLOSE,
                table.c.HIGH, table.c.LOW, table.c.VOLUME,
                table.c.VOLUME_USDT
            ).order_by(table.c.TIMESTAMP).all()
            return {
                col: [row[i] for row in query]
                for i, col in enumerate(
                    ['Date', 'Open', 'Close', 'High', 'Low', 'Volume', 'Volume Usdt']
                )
            }


    def save_charts(self, results_dict:dict) -> None:
        table = classes_dict[f'{self.instId}_{self.timeframe}'].__table__
        with Session() as session:
            try:
                for i in range(len(results_dict['Date'])):
                    target_data = session.query(exists().where(table.c.TIMESTAMP == results_dict['Date'][i])).scalar()
                    print(target_data)
                    if not target_data:
                        data = table(
                            TIMESTAMP=results_dict['Date'][i], INSTRUMENT=self.instId,
                            TIMEFRAME=self.timeframe, OPEN=results_dict['Open'][i],
                            CLOSE=results_dict['Close'][i], HIGH=results_dict['High'][i],
                            LOW=results_dict['Low'][i], VOLUME=results_dict['Volume'][i],
                            VOLUME_USDT=results_dict['Volume Usdt'][i]
                        )
                        session.add(data)
                        session.commit()
            except Exception as e:
                logger.error(f'{e}')
                session.rollback()
                raise e
            finally:
                session.close()
            


    # Добавление одной строки 
    def add_data_to_db(self, results_dict:dict) -> None:
        table = classes_dict[f'{self.instId}_{self.timeframe}'].__table__
        with Session() as session:
            data = table(
                TIMESTAMP=results_dict['Date'], INSTRUMENT=self.instId,
                TIMEFRAME=self.timeframe, OPEN=results_dict['Open'],
                CLOSE=results_dict['Close'], HIGH=results_dict['High'],
                LOW=results_dict['Low'], VOLUME=results_dict['Volume'],
                VOLUME_USDT=results_dict['Volume Usdt']
            )
            if not session.query(exists().where(table.c.TIMESTAMP == data.TIMESTAMP)).scalar():
                session.add(data)
            try:
                session.commit()
            except Exception as e:
                logger.error(f'{e}')
                session.rollback()
                raise e
            finally:
                session.close()


    def save_new_order_data(self, result:dict) -> None:
        with Session() as session:
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
            session.add(order_id)
            try:
                session.commit()
            except Exception as e:
                logger.error(f'{e}')
                session.rollback()
                raise e
            finally:
                session.close()



class StateRequest:
    def __init__(
        self, intsId:Optional[str]=None, timeframe:Optional[str]=None,
        strategy:Optional[str]=None
        ):
        self.instId = intsId
        self.timeframe = timeframe
        self.strategy = strategy


    def check_state(self) -> Optional[str]:
        with Session() as session:
            if last_state := session.query(SQLStateStorage).filter_by(
                INST_ID=self.instId, TIMEFRAME=self.timeframe,
                STRATEGY=self.strategy
                ).first():
                return last_state.POSITION
            return None


    def update_state(self, new_state:dict) -> None:
        with Session() as session:
            existing_state = session.query(SQLStateStorage).filter_by(
                INST_ID=self.instId, TIMEFRAME=self.timeframe
                ).first()
            existing_state.POSITION = new_state['state']
            existing_state.STATUS = new_state['status']
            existing_state.ORDER_ID = new_state['orderId']
            try:
                session.commit()
            except Exception as e:
                logger.error(f'{e}')
                session.rollback()
                raise e
            finally:
                session.close()


    def save_position_state(self, new_state:dict) -> None:
        with Session() as session:
            state = SQLStateStorage(
                INST_ID=self.instId, TIMEFRAME=self.timeframe, POSITION=new_state['state'],
                ORDER_ID=new_state['orderId'], STATUS=new_state['status']
            ) 
            session.add(state)
            try:
                session.commit()
            except Exception as e:
                logger.error(f'{e}')
                session.rollback()
                raise e
            finally:
                session.close()


    def save_none_state(self) -> None:
        with Session() as session:
            new_state = SQLStateStorage(
                INST_ID=self.instId, TIMEFRAME=self.timeframe, POSITION=None,
                ORDER_ID=None, STATUS=False, STRATEGY = self.strategy
            )
            session.add(new_state)
            try:
                session.commit()
            except Exception as e:
                logger.error(f'{e}')
                session.rollback()
                raise e
            finally:
                session.close()

