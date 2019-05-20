#coding=utf-8
import asyncio
import random
import time

class MockExecutor():

    def __init__(self, elp, delay=0.5):
        self.delay = delay

    def create_order(self, symbol, op, price, amount):
        time.sleep(self.delay)
        return (True,'mock id'+str(random.randint(10,999)))

    def submit_cancel(self, order_id):
        time.sleep(self.delay)
        return True

    def query_order_state(self, order_id):
        time.sleep(self.delay)
        return (True,'submitted')

class FcoinExecutor():

    def __init__(self, elp):
        # init aiofcoin
        from aiofcoin import FcoinAPI
        import config

        self.eloop = elp
        self.fcoin_obj = FcoinAPI( elp,
                config.key, config.secret, config.proxy)

        self.order_create_abbr = {'b': {'side': 'buy'}, 's': {'side': 'sell'},
                                  'l': {'type': 'limit'}, 'm': {'type': 'market'}}
    def __del__(self):
        self.eloop.run_until_complete(self.fcoin_obj.close_sess())

    def create_order(self, symbol, op, price, amount):
        params = {'symbol': symbol, 'price': price,
         'amount': amount, }

        for c in op:
            params.update(self.order_create_abbr[c])

        (state_code, json_obj) = self.eloop.run_until_complete(
            self.fcoin_obj.create_order(**params))

        if 'status' not in json_obj or 0 != json_obj['status']:
            return (False, None)
        else:
            return (True, json_obj['data'])

    def submit_cancel(self, order_id):
        (state_code, json_obj) = self.eloop.run_until_complete(
            self.fcoin_obj.submit_cancel_order(order_id))

        if 'status' not in json_obj or 0 != json_obj['status']:
            return (False, None)
        else:
            return (True, json_obj['data'])

    def query_order_state(self, order_id):
        (state_code, json_obj) = self.eloop.run_until_complete(
            self.fcoin_obj.query_order_by_id(order_id))

        if 'status' not in json_obj or 0 != json_obj['status']:
            return (False, None)
        else:
            return (True, json_obj['data']['state'])


if __name__ == '__main__':
    elp = asyncio.get_event_loop()
    exe = FcoinExecutor(elp)
    print(exe.query_order_state('gs8Vn0DSgtYQ7hu5zwZDQ54upRWGQIz8ij7f84j-PIBZ21KNYX26gjtBfMWgsjRR7sNUdV9-OTjCEjmLrDUJPw=='))
