#coding=utf-8

import asyncio
import aiohttp
import time


class WSFcoinFeeder():

    def __init__(self, proxy=None):
        self.ws_url = 'wss://api.fcoin.com/v2/ws'
        self.proxy = proxy
        self.ws = None

    async def feeding(self, topics):
        if not isinstance(topics, list):
            topics = [topics]

        async with aiohttp.ClientSession() as session:
            self.ws = await session.ws_connect(self.ws_url, proxy=self.proxy)
            hello_msg = await self.ws.receive_json()

            d = {"cmd": "sub", "args": topics, "id": "fcmd_id"}
            await self.ws.send_json(d)
            d = {"cmd": "ping", "args": [time.time_ns()], "id": "fcmd_id"}
            await self.ws.send_json(d)
            async for msg in self.ws:
                jo = msg.json()

                if jo['type'] == 'ping':
                    asyncio.create_task(
                        self._send_ws_heartbeat_with_delay(self.ws))
                    continue

                if jo['type'] in topics:
                    yield jo
                # ignore the rest kind of msg

    async def _send_ws_heartbeat_with_delay(self, ws, delay=30):
        await asyncio.sleep(delay)

        d = {"cmd": "ping", "args": [time.time_ns()], "id": "fcmd_id"}
        await ws.send_json(d)


    async def close(self):
        if self.ws and not self.ws.closed:
            await self.ws.close()
