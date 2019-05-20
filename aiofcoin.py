# -*- coding:utf-8 -*-

import asyncio
import aiohttp
import hmac
import hashlib
import base64
import ssl
import time

POST = 'POST'
GET = 'GET'


class FcoinAPI():
    def __init__(self, elp, key='', secret='', proxy=None):

        api_address = 'api.fcoin.com'
        crt_path = 'sca1b.crt'

        self.http = 'https://%s/v2/' % api_address
        self.http_orders = self.http+'orders/'
        self.http_market = self.http+'market/'
        self.http_otc = self.http+'broker/otc/'
        self.key = key
        self.secret = secret.encode('utf-8')
        self.proxy = proxy
        self.sslcontext = ssl.create_default_context(
            ssl.Purpose.CLIENT_AUTH, capath=crt_path)
        
        self.sess = aiohttp.ClientSession(loop=elp)

    async def close_sess(self):
        await self.sess.close()

    async def signed_request(self, method, url, **params):
        param = ''
        if params:
            sort_pay = sorted(params.items(), key=lambda x: x[0])
            var_list = list()
            for k in sort_pay:
                var_list.append('{}={}'.format(str(k[0]), str(k[1])))
            param = '&'.join(var_list)

        timestamp = str(int(time.time() * 1000))

        if method == GET:
            if param:
                url = url + '?' + param
            sig_str = method + url + timestamp
        elif method == POST:
            sig_str = method + url + timestamp + param

        # double b64encode
        sig_str = base64.b64encode(sig_str.encode('utf-8'))
        signature = base64.b64encode(
            hmac.new(self.secret, sig_str, digestmod=hashlib.sha1).digest())

        headers = {
            'FC-ACCESS-KEY': self.key,
            'FC-ACCESS-SIGNATURE': signature.decode('utf-8'),
            'FC-ACCESS-TIMESTAMP': timestamp
        }

        async with self.sess.request(method, url, ssl=self.sslcontext,
                                proxy=self.proxy, headers=headers, json=params) as resp:
            return resp.status, await resp.json(content_type=None)

    async def public_request(self, method, url, **params):
        param = ''
        if params:
            sort_pay = sorted(params.items(), key=lambda x: x[0])
            var_list = list()
            for k in sort_pay:
                var_list.append('{}={}'.format(str(k[0]), str(k[1])))
            param = '&'.join(var_list)

        timestamp = str(int(time.time() * 1000))

        if method == GET:
            if param:
                url = url + '?' + param

        async with self.sess.request(method, url, ssl=self.sslcontext,
                                proxy=self.proxy, json=params) as resp:
            return resp.status, await resp.json(content_type=None)

    async def query_trading_balance(self):
        """trading account balance"""
        return await self.signed_request(GET, self.http+'accounts/balance')

    async def query_wallet_balance(self):
        """trading account balance"""
        return await self.signed_request(GET, self.http+'assets/accounts/balance')

    async def trans_wallet2trading(self, currency, amount):
        url = self.http+'assets/accounts/assets-to-spot'
        params = {'currency': currency, 'amount': amount}
        return await self.signed_request(POST, url, **params)

    async def trans_trading2wallet(self, currency, amount):
        url = self.http+'accounts/spot-to-assets'
        params = {'currency': currency, 'amount': amount}
        return await self.signed_request(POST, url, **params)

    async def query_market_ticker(self, symbol):
        url = self.http_market+'ticker/{}'.format(symbol)
        return await self.public_request(GET, url)

    async def query_market_depth(self, symbol, level):
        url = self.http_market+'depth/{}/{}'.format(level, symbol)
        return await self.public_request(GET, url)

    async def query_market_trades(self, symbol, limit=20):
        url = self.http_market+'trades/{}'.format(symbol)
        params = {'limit': limit}
        return await self.public_request(GET, url, **params)

    async def query_market_candle(self, symbol, resolution, limit=20):
        url = self.http_market+'candles/{}/{}'.format(resolution, symbol)
        params = {'limit': limit}
        return await self.public_request(GET, url, **params)

    async def query_market_all_tickers(self):
        url = self.http_market+'all-tickers'
        return await self.public_request(GET, url)

    async def query_orders(self, symbol, states='submitted,partial_filled', limit=20):
        url = self.http_orders
        params = {'symbol': symbol, 'limit': limit, 'states': states}
        return await self.signed_request(GET, url, **params)

    async def query_order_by_id(self, order_id):
        url = self.http_orders+order_id
        return await self.signed_request(GET, url)

    async def query_order_match_results(self, order_id):
        url = self.http_orders+order_id+'/match-results'
        return await self.signed_request(GET, url)

    async def submit_cancel_order(self, order_id):
        url = self.http_orders+order_id+'/submit-cancel'
        params = {'order_id': order_id}
        return await self.signed_request(POST, url, **params)

    async def create_order(self, symbol, side, type, price, amount, exchange='main'):
        url = self.http_orders
        params = {'symbol': symbol, 'exchange': exchange, 'side': side, 'type': type,
                  'price': price, 'amount': amount}
        return await self.signed_request(POST, url, **params)

    async def trans_in_otc(self, currency, amount, account_type):
        url = self.http_otc+'assets/transfer/in'
        params = {'currency': currency, 'amount': amount,
                  'source_account_type': account_type, 'target_account_type': 'otc'}
        return await self.signed_request(POST, url, **params)

    async def trans_out_otc(self, currency, amount, account_type):
        url = self.http_otc+'assets/transfer/out'
        params = {'currency': currency, 'amount': amount,
                  'source_account_type': 'otc', 'target_account_type': account_type}
        return await self.signed_request(POST, url, **params)

    async def otc_users(self):
        url = self.http_otc+'users'
        return await self.signed_request(GET, url)

    async def query_otc_balance(self):
        url = self.http_otc+'users/me/balances'
        return await self.signed_request(GET, url)

    async def query_otc_balance_by_currency(self, currency):
        url = self.http_otc+'users/me/balance'
        return await self.signed_request(GET, url, currency=currency)

    async def query_otc_suborders(self, states):
        url = self.http_otc+'suborders'
        params = {'states': states}
        return await self.signed_request(GET, url, **params)

    async def query_otc_suborder(self, id):
        url = self.http_otc+'suborders/{}'.format(id)
        return await self.signed_request(GET, url)

    async def query_otc_delegation_order(self, id):
        url = self.http_otc+'delegation_orders/{}'.format(id)
        return await self.signed_request(GET, url)
