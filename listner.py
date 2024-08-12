#!/usr/bin/env python3
import asyncio
from WebSockets.OKXWebsocketsChannel import OKXWebsocketsChannel
from DataSets.DataBaseAsync import create_async_engine

async def main():
    await create_async_engine()
    await OKXWebsocketsChannel('ANY', True, True, True).subscribe_to_updates()


okx_channel = OKXWebsocketsChannel()
if __name__ == '__main__':
    asyncio.run(main())