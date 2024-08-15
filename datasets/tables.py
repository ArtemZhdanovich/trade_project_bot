#libs
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric, Boolean, Float
from sqlalchemy.sql import text
from sqlalchemy.orm import declarative_base, sessionmaker
#configs
from configs.load_settings import LoadUserSettingData


Base = declarative_base()


class ClassCreation:
    def __init__(self):
        self.user_settings = LoadUserSettingData().load_user_settings()


    def create_classes(self, Base):
        classes = {}
        for inst_id in self.user_settings['instIds']:
            for timeframe in self.user_settings['timeframes']:
                class_name = f"{inst_id}_{timeframe}"
                table_name = f"{inst_id}_{timeframe}"
                class_ = type(class_name, (Base,), {
                    '__tablename__': table_name,
                    '__table_args__': {'extend_existing': True},
                    'TIMESTAMP': Column(DateTime, primary_key=True),
                    'INSTRUMENT': Column(String),
                    'TIMEFRAME': Column(String),
                    'OPEN': Column(Numeric(30,10)),
                    'CLOSE': Column(Numeric(30,10)),
                    'HIGH': Column(Numeric(30,10)),
                    'LOW': Column(Numeric(30,10)),
                    'VOLUME': Column(Numeric(30,10)),
                    'VOLUME_USDT': Column(Numeric(30,10))
                })
                classes[class_name] = class_
        return classes


#добавлена автоинкрементируемая ячейка для создания доступа к таймфрему в процессе родителе
#теперь при создании объекта ордера, доступ к данным таймфрема можно будет получить по 
# уникальному инкрементируемому id(в теории)-> Похуй
class PositionAndOrders(Base):
    __tablename__ = 'positions_and_orders'
    ID = Column(Integer, autoincrement=True, primary_key=True)
    ORDER_ID = Column(String, nullable=False)
    INSTRUMENT = Column(String)
    SIDE_OF_TRADE = Column(String)
    LEVERAGE = Column(Integer)
    OPEN_TIME = Column(DateTime)
    CLOSE_TIME = Column(DateTime, nullable=True)
    STATUS = Column(Boolean)
    BALANCE = Column(Integer)
    PRICE_OF_CONTRACT = Column(Float)
    NUMBER_OF_CONTRACTS = Column(Float)
    MONEY_IN_DEAL = Column(Float, nullable=True)
    ENTER_PRICE = Column(Float, nullable=True)
    ORDER_VOLUME = Column(Float)
    TAKEPROFIT_PRICE = Column(Float, nullable=True)
    TAKEPROFIT_ORDER_ID = Column(String, nullable=True)
    TAKEPROFIT_ORDER_VOLUME = Column(Float, nullable=True)
    STOPLOSS_PRICE = Column(Float)
    STOPLOSS_ORDER_ID = Column(String)
    STOPLOSS_ORDER_VOLUME = Column(Float)
    RISK_COEFFICIENT = Column(Float)
    CLOSE_PRICE = Column(Float, nullable=True)
    FEE = Column(Float, nullable=True)
    MONEY_INCOME = Column(Float, nullable=True)
    PERCENT_MONEY_INCOME = Column(Float, nullable=True)



class SQLStateStorage(Base):
    __tablename__ = 'States'
    __table_args__ = {'extend_existing': True}
    ID = Column(Integer, primary_key=True, autoincrement=True)
    INST_ID = Column(String)
    TIMEFRAME = Column(String)
    POSITION = Column(String, nullable=True)
    ORDER_ID = Column(String, nullable=True)
    STRATEGY = Column(String)
    STATUS = Column(Boolean)


engine = create_engine('postgresql://postgres:admin1234@localhost/trade_user_data')
classes_dict = ClassCreation().create_classes(Base)
Base.metadata.create_all(engine)