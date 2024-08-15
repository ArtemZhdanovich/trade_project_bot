#libs
from typing import Optional
#database
from datasets.tables import SQLStateStorage
from datasets.database import Session
#utils
from baselogs.custom_logger import create_logger


logger = create_logger('StatesDb')


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
        # sourcery skip: class-extract-method
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



