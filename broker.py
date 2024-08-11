#!/usr/bin/env python3
from Configs.LoadSettings import LoadUserSettingData
from Listner.IventListner import OKXIventListner


if __name__ == '__main__':
    settings = LoadUserSettingData().load_user_settings()
    listner_instance = OKXIventListner(settings['instIds'][1], settings['timeframes'][0])
    listner_instance.create_listner()
