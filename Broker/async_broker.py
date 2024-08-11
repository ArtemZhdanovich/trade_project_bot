#!/usr/bin/env python3
import asyncio
from Configs.LoadSettings import LoadUserSettingData
from Listner.IventListnerAsync import OKXIventListnerAsync

settings = LoadUserSettingData().load_user_settings()

async def main(settings:dict):
    listner_instance = OKXIventListnerAsync(settings['instIds'][1], settings['timeframes'][0])
    listner_instance.create_listner()

if __name__ == '__main__':
    asyncio.run(main(settings))