#!/usr/bin/env python3
import time
from threading import Thread
import schedule
from User.LoadSettings import LoadUserSettingData
from utils.StartDelayCalculator import StartDelayCalc
from User.Signals import AVSL_RSI_ClOUDS


settings = LoadUserSettingData.load_user_settings()
scriner_instance1 = AVSL_RSI_ClOUDS(settings['instIds'][0], settings['timeframes'][0], 300)
scriner_instance1.add_data_to_redis()
scriner_instance2 = AVSL_RSI_ClOUDS(settings['instIds'][0], settings['timeframes'][1], 300)
scriner_instance2.add_data_to_redis()
scriner_instance3 = AVSL_RSI_ClOUDS(settings['instIds'][0], settings['timeframes'][2], 300)
scriner_instance3.add_data_to_redis()
scriner_instance4 = AVSL_RSI_ClOUDS(settings['instIds'][0], settings['timeframes'][3], 300)
scriner_instance4.add_data_to_redis()


def check_signal(scriner_instance):
    state = scriner_instance.check_active_state()
    if state is None:
        scriner_instance.create_signals()
    elif state:
        scriner_instance.trailing_stoploss()


def run_job(job_func, arg):
    job_thread = Thread(target=job_func, args=(arg,))
    job_thread.start()


schedule.every(20).seconds.do(run_job, check_signal, scriner_instance1)
schedule.every(40).seconds.do(run_job, check_signal, scriner_instance2)
schedule.every(60).seconds.do(run_job, check_signal, scriner_instance3)
schedule.every(80).seconds.do(run_job, check_signal, scriner_instance4)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    #StartDelayCalc.startdelay()
    thread = Thread(target=run_schedule)
    thread.start()
