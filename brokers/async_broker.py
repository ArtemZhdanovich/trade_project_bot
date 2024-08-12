#!/usr/bin/env python3
import asyncio
from configs.load_settings import LoadUserSettingData
from listners.ivent_listner_async import OKXIventListnerAsync

settings = LoadUserSettingData().load_user_settings()

async def main(settings:dict):
    listner_instance = OKXIventListnerAsync(settings['instIds'][1], settings['timeframes'][0])
    listner_instance.create_listner()

if __name__ == '__main__':
    asyncio.run(main(settings))