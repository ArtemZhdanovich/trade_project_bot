#!/usr/bin/env python3
from configs.load_settings import LoadUserSettingData
from listners.ivent_listner import OKXIventListner


if __name__ == '__main__':
    settings = LoadUserSettingData().load_user_settings()
    listner_instance = OKXIventListner(settings['instIds'][1], settings['timeframes'][0])
    listner_instance.create_listner()
