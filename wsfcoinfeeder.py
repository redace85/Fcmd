#coding=utf-8

import asyncio
import aiohttp
import time
import ssl


class WSFcoinFeeder():

    def __init__(self, elp, proxy=None, use_ifukang=False):
        if use_ifukang:
            self.ws_url = 'wss://api.ifukang.com/v2/ws'
        else:
            self.ws_url = 'wss://api.fcoin.com/v2/ws'
        self.proxy = proxy
        self.ws = None

        crt_path = 'sca1b.crt'
        self.sslcontext = ssl.create_default_context(
            ssl.Purpose.CLIENT_AUTH, capath=crt_path)

        self.sess = aiohttp.ClientSession(loop=elp)

        self.topics = []

    async def con_sub(self, topics):
        if not isinstance(topics, list):
            self.topics = [topics]
        else:
            self.topics = topics

        self.ws = await self.sess.ws_connect(self.ws_url, ssl=self.sslcontext,
                                            proxy=self.proxy)
        
        # hello msg
        _ = await self.ws.receive_json()

        ol = [{"cmd": "sub", "args": self.topics, "id": "fcmd_id"},
        {"cmd": "ping", "args": [int(time.time()*1000)], "id": "fcmd_id"}]
        for o in ol:
            await self.ws.send_json(o)

    async def feed_stream(self):
        if self.ws is None:
            return
        async for msg in self.ws:
            jo = msg.json()
            #print('jo:',jo)

            if jo['type'] == 'ping':
                asyncio.create_task(
                    self._send_ws_heartbeat_with_delay(self.ws))
                continue

            if jo['type'] in self.topics:
                yield jo
            # ignore the rest kind of msg

    async def all_tickers_stream(self):
        if self.ws is None:
            return
        async for msg in self.ws:
            jo = msg.json()

            if 'topic' in jo and 'all-tickers' == jo['topic']:
                yield jo
            elif jo['type'] == 'ping':
                asyncio.create_task(
                    self._send_ws_heartbeat_with_delay(self.ws))
                continue

    async def _send_ws_heartbeat_with_delay(self, ws, delay=10):
        await asyncio.sleep(delay)

        lt = int(time.time()*1000)
        d = {"cmd": "ping", "args": [lt], "id": "fcmd_id"}
        await ws.send_json(d)

    async def req_topic(self, topic, limit=10):
        '''
        only candle and market trade record works
        '''
        if self.ws:
            o = {"cmd": "req", "args": [topic,limit], "id": "fcmd_id"}
            await self.ws.send_json(o)

    async def close(self):
        if self.ws and not self.ws.closed:
            await self.ws.close()
        await self.sess.close()