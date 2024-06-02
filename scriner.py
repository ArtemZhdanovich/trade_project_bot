#!/usr/bin/env python3
import asyncio, time
from threading import Thread
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import schedule
from datasets.database import DataAllDatasets
from User.LoadSettings import LoadUserSettingData
from utils.StartDelayCalculator import StartDelayCalc


# Загрузка пользовательских настроек
flag, timeframes, instIds, passphrase, api_key, secret_key, host, db, port = LoadUserSettingData.load_user_settings()

# Настройка подключения к базе данных
engine = create_engine("sqlite:///C:\\Users\\Admin\\Desktop\\trade_project_bot\\datasets\\TradeUserDatasets.db")
Base = declarative_base()

# Создание классов и таблиц
data_all_datasets = DataAllDatasets(instIds, flag, timeframes)
classes_dict = data_all_datasets.create_classes(Base)
TradeSignals = data_all_datasets.create_TradeUserData(Base)
Base.metadata.create_all(engine)
print(f'\n\n{classes_dict}\n\n')
# Создание сессии
Session = sessionmaker(bind=engine)


# Функция для запуска задачи в отдельном потоке
def run_job(job_func):
    job_thread = Thread(target=job_func)
    job_thread.start()


schedule.every(15).minutes.do(run_job, DataAllDatasets.get_current_chart_data(
            flag, instIds[1], timeframes[0], Base, Session, classes_dict,
            load_data_after = None, load_data_before = None,
            lenghts = 100
            ))


schedule.every(1).hours.do(run_job, DataAllDatasets.get_current_chart_data(
            flag, instIds[1], timeframes[1], Base, Session, classes_dict,
            load_data_after=None, load_data_before=None,
            lenghts=100
            ))


schedule.every(4).hours.do(run_job, DataAllDatasets.get_current_chart_data(
            flag, instIds[1], timeframes[2], Base, Session, classes_dict,
            load_data_after=None, load_data_before=None,
            lenghts=100
            ))


schedule.every(1).days.do(run_job, DataAllDatasets.get_current_chart_data(
            flag, instIds[1], timeframes[3], Base, Session, classes_dict,
            load_data_after = None, load_data_before = None,
            lenghts = 100
            ))


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)




message = '415 база ответьте'

# Асинхронная функция для отправки сообщений каждые 15 секунд
async def send_messages_periodically(message, host, port, db):
    while True:
        LoadUserSettingData.publish_message('my-channel',message, host, port, db)
        print('сообщение отправлено')
        await asyncio.sleep(15)  # Ожидание 15 секунд

if __name__ == "__main__":
    #StartDelayCalc.startdelay()
    thread = Thread(target=run_schedule)
    thread.start()
    # Запуск асинхронной функции
    asyncio.run(send_messages_periodically(message, host, port, db))


    
