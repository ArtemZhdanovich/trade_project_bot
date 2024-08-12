#!/usr/bin/env python3
import asyncio
from websockets_sub.okx_websockets_channel import OKXWebsocketsChannel
from datasets.database_async import create_tables


async def main():
    await create_tables()
    await OKXWebsocketsChannel('ANY', True, True, True).subscribe_to_updates()


okx_channel = OKXWebsocketsChannel()
if __name__ == '__main__':
    asyncio.run(main())