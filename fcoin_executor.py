#coding=utf-8
import asyncio
import random
import time


class FcoinExecutor():

    def __init__(self, elp, mock_trade=False, delay=1):
        # init aiofcoin
        from aiofcoin import FcoinAPI
        import config

        self.mock_trade = mock_trade
        self.delay = delay
        self.eloop = elp
        self.fcoin_obj = FcoinAPI( elp,
                config.key, config.secret, config.proxy, config.use_ifukang)

        self.order_create_abbr = {'b': {'side': 'buy'}, 's': {'side': 'sell'},
                                  'l': {'type': 'limit'}, 'm': {'type': 'market'}}
    def __del__(self):
        self.eloop.run_until_complete(self.fcoin_obj.close_sess())

    def create_order(self, symbol, op, price, amount):
        # mock trade
        if self.mock_trade:
            time.sleep(self.delay)
            return (True,'mock id'+str(random.randint(10,999)))

        params = {'symbol': symbol, 'price': price,
         'amount': amount, }

        for c in op:
            params.update(self.order_create_abbr[c])

        (state_code, json_obj) = self.eloop.run_until_complete(
            self.fcoin_obj.create_order(**params))

        if 200!= state_code or 'status' not in json_obj or 0 != json_obj['status']:
            return (False, None)
        else:
            return (True, json_obj['data'])

    def submit_cancel(self, order_id):
        # mock trade
        if self.mock_trade:
            time.sleep(self.delay)
            return True

        (state_code, json_obj) = self.eloop.run_until_complete(
            self.fcoin_obj.submit_cancel_order(order_id))

        if 200!= state_code or 'status' not in json_obj or 0 != json_obj['status']:
            return False
        else:
            return True

    def query_order(self, order_id):
        # mock trade
        if self.mock_trade:
            time.sleep(self.delay)
            return (True,'submitted')

        (state_code, json_obj) = self.eloop.run_until_complete(
            self.fcoin_obj.query_order_by_id(order_id))

        if 200!= state_code or 'status' not in json_obj or 0 != json_obj['status']:
            return (False, None)
        else:
            return (True, json_obj['data'])

    def query_available_tb(self, symbols):

        (state_code, json_obj) = self.eloop.run_until_complete(
            self.fcoin_obj.query_trading_balance())

        if 200!= state_code or 'status' not in json_obj or 0 != json_obj['status']:
            return (False, None)
        else:
            a_tb_dict = dict()
            for o in json_obj['data']:
                c = o['currency']
                if c in symbols:
                    a_tb_dict[c] = o['available']
                    symbols.remove(c)
                    if 0 == len(symbols):
                        break
            
            return (True, a_tb_dict)

    def query_dp_l20(self, symbol):

        (state_code, json_obj) = self.eloop.run_until_complete(
            self.fcoin_obj.query_market_depth(symbol,'L20'))

        if 200!= state_code or 'status' not in json_obj or 0 != json_obj['status']:
            return (False, None)
        else:
            return (True, json_obj['data'])