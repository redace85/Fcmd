#!/usr/bin/env python3
#coding=utf-8
from cmd import Cmd
import time
import asyncio
# local modules below
import aiofcoin
import config

class FcmdObj(Cmd):
    intro = '''
                   ___         ___           ___          _____
                  /  /\       /  /\         /__/\        /  /::\\
                 /  /:/_     /  /:/        |  |::\      /  /:/\:\\
                /  /:/ /\   /  /:/         |  |:|:\    /  /:/  \:\\
               /  /:/ /:/  /  /:/  ___   __|__|:|\:\  /__/:/ \__\:|
              /__/:/ /:/  /__/:/  /  /\ /__/::::| \:\ \  \:\ /  /:/
              \  \:\/:/   \  \:\ /  /:/ \  \:\~~\__\/  \  \:\  /:/
               \  \::/     \  \:\  /:/   \  \:\         \  \:\/:/
                \  \:\      \  \:\/:/     \  \:\         \  \::/
                 \  \:\      \  \::/       \  \:\         \__\/
                  \__\/       \__\/         \__\/

A interactive cli for fcoin
type ? to list the available cmds'''

    prompt = 'Fcmd:>> '

    def __init__(self):
        Cmd.__init__(self)
        print('setting up env ...')

        self.fcoin_obj = aiofcoin.FcoinAPI(
        config.key,config.secret,config.proxy)

        self.otc_account_type={'w':'assets','t':'exchange'}
        self.order_list_abbr = {'s':'submitted','f':'filled','c':'canceled'}
        self.order_create_abbr = {'b':{'side':'buy'},'s':{'side':'sell'},
        'l':{'type':'limit'},'m':{'type':'market'}}
        self.order_pos_cache=list()
        print('env ready')

    def do_exit(self, arg):
        '''Exit Fcmd, shorthand: x'''
        print('Bye')
        return True

    # shorthand x for exit
    do_x = do_exit

    def __handle_aio_result(self, aw_obj, print_func):
        async def aiofunc():
            try:
                print_func(*(await aw_obj))
            except Exception as e:
                print(e)
        asyncio.run(aiofunc())

    def __common_print_func(self, state_code, json_obj):
        print('state_code:{}\n'.format(state_code))
        if 'status' not in json_obj or \
         ( 0!= json_obj['status'] and 'ok'!=json_obj['status']):
            print(json_obj)
        else:
            print('Operation Succeed!')

    def do_tb(self, arg):
        '''Query trading account balance
        Args:
            clist:a list of names of currencies, return all non-zero if not given
        Example:
            # query btc and tf balance of trading account
            :>>tb btc eth eos ft
        '''
        currencies = []
        if arg:
            currencies = arg.split(' ')

        def print_tb(state_code,json_obj):
            if 'status' not in json_obj or 0!= json_obj['status']:
                print(json_obj)
                return
            res_str = ''
            line_pattern = '{:6}:b:{:},a:{},f:{}\n'

            if 0==len(currencies):
                for o in json_obj['data']:
                    if '0.000000000000000000' != o['available']:
                        res_str += line_pattern.format(o['currency'],
                        o['balance'],o['available'],o['frozen'])
            else:
                for o in json_obj['data']:
                    c = o['currency']
                    if c in currencies:
                        res_str += line_pattern.format(c,
                        o['balance'],o['available'],o['frozen'])

                        currencies.remove(c)
                        if 0==len(currencies):
                            break

            print(res_str)

        self.__handle_aio_result(self.fcoin_obj.query_trading_balance(), print_tb)

    def do_w2t(self, arg):
        '''Transfer assets from mywallet to trading account
        Args:
            currency: name of the crypto currency
            amount: amount to transfer
        Example:
            # transfer 1000 ft from my wallet to trading account
            :>>w2t ft 1000
        '''
        if not arg:
            print('argments is needed')
            return

        args = arg.split(' ')
        if 2 != len(args):
            print('2 args are needed')
            return

        self.__handle_aio_result(self.fcoin_obj.trans_mywallet2trading(args[0],args[1]),
         self.__common_print_func)

    def do_ci(self, arg):
        '''Transfer assets into otc account
        Args:
            account_type: (w)wallet; (t)trading account
            currency: name of the crypto currency
            amount: amount to transfer
        Example:
            # transfer 100 usdt from trading account to otc account
            :>>ci t usdt 100
        '''
        if not arg:
            print('argments is needed')
            return

        args = arg.split(' ')
        if 3 != len(args):
            print('3 args are needed')
            return
        if args[0] not in self.otc_account_type:
            print('wrong account_type!')
            return
        at = self.otc_account_type[args[0]]

        self.__handle_aio_result(self.fcoin_obj.trans_in_otc(args[1],args[2],at),
         self.__common_print_func)


    def do_co(self, arg):
        '''Transfer assets out of otc account
        Args:
            account_type: (w)wallet; (t)trading account
            currency: name of the crypto currency
            amount: amount to transfer
        Example:
            # transfer 100 usdt from otc account to trading account
            :>>co t usdt 100
        '''
        if not arg:
            print('argments is needed')
            return

        args = arg.split(' ')
        if 3 != len(args):
            print('3 args are needed')
            return
        if args[0] not in self.otc_account_type:
            print('wrong account_type!')
            return
        at = self.otc_account_type[args[0]]

        self.__handle_aio_result(self.fcoin_obj.trans_out_otc(args[1],args[2],at),
         self.__common_print_func)

    def do_cb(self, arg):
        '''Query otc account balance
        Args:
            None
        Example:
            :>>cb
        '''
        def print_ob(state_code,json_obj):
            if 'status' not in json_obj or 'ok'!= json_obj['status']:
                print(json_obj)
                return
            res_str = 'summary_aprox_btc:{}\n'.format(json_obj['data']['summary'])
            line_pattern = '{:6}:a:{},f:{}\n'

            for o in json_obj['data']['balances']:
                res_str += line_pattern.format(o['currency'],
                o['available_amount'],o['frozen_amount'])

            print(res_str)

        self.__handle_aio_result(self.fcoin_obj.query_otc_balance(),print_ob)

    def do_mtk(self, arg):
        '''Query ticker information of currency/usdt pair
        Args:
            currency: name of the crypto currency
        Example:
            :>>mtk btc
        '''
        def print_mtk(state_code,json_obj):
            if 'status' not in json_obj or 0!= json_obj['status']:
                print(json_obj)
                return
            d = json_obj['data']
            res_str = 'seq:{} type:{}\n'.format(d['seq'],d['type'])
            res_str += 'np:{} nv:{}\nbp1:{} bv1:{} sp1:{} sv1:{}\n\
24bp:{} 24hp:{} 24lp:{}\n24cv:{} 24uv:{}\n'.format(*d['ticker'])

            print(res_str)

        if not arg:
            print('argments is needed')
            return

        self.__handle_aio_result(self.fcoin_obj.query_market_ticker(arg+'usdt'),print_mtk)

    def do_mdp(self, arg):
        '''Query depth information of currency/usdt pair
        Args:
            currency: name of the crypto currency
            depth: number of depth information 20 or 150
        Example:
            # query L20 depth info of btcusdt
            :>>mdp btc 20
        '''
        def print_mdp(state_code,json_obj):
            if 'status' not in json_obj or 0!= json_obj['status']:
                print(json_obj)
                return
            d = json_obj['data']
            res_str = 'seq:{} type:{} time:{}\n'.format(
            d['seq'],d['type'],time.ctime(d['ts']/1000))

            c_bid, c_ask = 0.0, 0.0
            for i, (bid,ask) in enumerate(zip(d['bids'],d['asks'])):
                if 0==i%2:
                    c_bid, c_ask = bid, ask
                else:
                    res_str += 'bp:{:9} bv:{:9} sp:{:9} sv:{:9}\n'.format(
                    c_bid, bid, c_ask, ask)
            print(res_str)

        if not arg:
            print('argments is needed')
            return
        args = arg.split(' ')
        if 2 != len(args):
            print('2 args are needed')
            return

        self.__handle_aio_result(self.fcoin_obj.query_market_depth(
        args[0]+'usdt','L'+args[1],),print_mdp)

    def do_mtr(self, arg):
        '''Query trade information of currency/usdt pair
        Args:
            currency: name of the crypto currency
            limit: number of information
        Example:
            # query 10 traded info of btcusdt
            :>>mtr btc 10
        '''
        def print_mtr(state_code,json_obj):
            if 'status' not in json_obj or 0!= json_obj['status']:
                print(json_obj)
                return
            res_str = ''
            lp = '{}: {:<4}-> p:{:9} v:{:9}\n'
            for o in json_obj['data']:
                res_str += lp.format(time.ctime(o['ts']/1000),o['side'],
                o['price'],o['amount'])
            print(res_str)

        if not arg:
            print('argments is needed')
            return
        args = arg.split(' ')
        if 2 != len(args):
            print('2 args are needed')
            return

        self.__handle_aio_result(self.fcoin_obj.query_market_trades(
        args[0]+'usdt',int(args[1])),print_mtr)

    def do_mca(self, arg):
        '''Query trade candles info of currency/usdt pair
        Args:
            currency: name of the crypto currency
            resolution: M1 M3 M5 M15 M30 H1 H4 H6 D1 W1
            limit: number of information
        Example:
            # query 10 infos of candle.btcusdt.M15
            :>>mca btc M15 10
        '''
        def print_mca(state_code,json_obj):
            if 'status' not in json_obj or 0!= json_obj['status']:
                print(json_obj)
                return
            res_str = ''
            lp = '{}: o:{:9} c:{:9} h:{:9} l:{:9} n:{:6} bv:{:9} qv:{:9}\n'
            for o in json_obj['data']:
                res_str += lp.format(o['seq'],
                o['open'],o['close'],o['high'],o['low'],
                o['count'],o['base_vol'],o['quote_vol'])
            print(res_str)

        if not arg:
            print('argments is needed')
            return
        args = arg.split(' ')
        if 3 != len(args):
            print('3 args are needed')
            return

        self.__handle_aio_result(self.fcoin_obj.query_market_candle(
        args[0]+'usdt',args[1],int(args[2])),print_mca)

    def __handle_ol(self,state_code,json_obj):
        if 'status' not in json_obj or 0!= json_obj['status']:
            print(json_obj)
            return
        self.order_pos_cache.clear()
        res_str = ''
        lp = 'p{}->{} {} s:{} {}_{} am:{:.2f} fa:{:.2f}\n\
p:{:9} ev:{:9} ff:{:9} fi:{:9}\n'
        for i,o in enumerate(json_obj['data']):
            res_str += lp.format(i, time.ctime(o['created_at']/1000),
            o['symbol'],o['state'],o['side'],o['type'],
            float(o['amount']),float(o['filled_amount']),
            o['price'],o['executed_value'],o['fill_fees'],o['fees_income'])
            self.order_pos_cache.append(o['id'])
        res_str +='position cached!!!'
        print(res_str)

    def do_ol(self, arg):
        '''List orders of currency/usdt pair
        order position will be cached,and be used by other cmd etc:omr
        Args:
            currency: name of the crypto currency
            states: (s)submitted,(f)filled,(c)canceled, default f
            limit: number of information
        Example:
            # list 20 infos of submitted orders of btcusdt
            :>>ol btc
            # list 10 infos of submitted and filled orders
            :>>ol btc sf 10
        '''
        if not arg:
            print('argments is needed')
            return

        args = arg.split(' ')
        params = dict()
        for i, ar in enumerate(args):
            if 0==i:
                params['symbol'] = args[i]+'usdt'
            elif 1==i:
                st_list = list()
                for c in args[i]:
                    if c in self.order_list_abbr:
                        st_list.append(self.order_list_abbr[c])
                if len(st_list)>0:
                    params['states'] = ','.join(st_list)
            elif 2==i:
                params['limit'] = int(args[i])

        self.__handle_aio_result(self.fcoin_obj.query_orders(**params),self.__handle_ol)

    def do_omr(self, arg):
        '''Query match results of an order
        position cache must be generated by ol cmd first
        Args:
            pos: position start from 0; default 0
        Example:
            # equal to omr 0
            :>>omr
            # query the order at pos 1
            :>>omr 1
        '''
        def print_omr(state_code,json_obj):
            if 'status' not in json_obj or 0!= json_obj['status']:
                print(json_obj)
                return

            res_str = ''
            lp = '{} {}: fa:{:.2f} p:{:9} ff:{:9} fi:{:9}\n'
            for o in json_obj['data']:
                res_str += lp.format(time.ctime(o['created_at']/1000),
                o['type'], float(o['filled_amount']),o['price'],
                o['fill_fees'],o['fees_income'])
            print(res_str)

        if not arg:
            pos = 0
        else:
            pos = int(arg)
        if pos>=len(self.order_pos_cache):
            print('id not found')
            return

        self.__handle_aio_result(self.fcoin_obj.query_order_match_results(
        self.order_pos_cache[pos]),print_omr)

    def do_osc(self, arg):
        '''Submit cancel order cmd
        position cache must be generated by ol cmd first
        Args:
            pos: position start from 0; default 0
        Example:
            # equal to omr 0
            :>>osc
            # submit cancel order at pos 1
            :>>osc 1
        '''
        if not arg:
            pos = 0
        else:
            pos = int(arg)
        if pos>=len(self.order_pos_cache):
            print('id not found')
            return

        self.__handle_aio_result(self.fcoin_obj.submit_cancel_order(
        self.order_pos_cache[pos]),self.__common_print_func)

    def do_oc(self, arg):
        '''create order of currency/usdt pair
        Args:
            currency: name of the crypto currency
            op: (lb)limit buy; (mb) market buy; (ls)limit sell; (ms)market sell
            price: the price
            amount: amount of currency to operate
        Example:
            # limit sell 900 ft at price 0.10100
            :>>oc ft ls 0.10100 900
        '''
        if not arg:
            print('argments is needed')
            return

        args = arg.split(' ')
        if 4 != len(args):
            print('4 args are needed')
            return

        params = {'symbol':args[0]+'usdt','price':args[2],'amount':args[3]}

        for c in args[1]:
            params.update(self.order_create_abbr[c])

        self.__handle_aio_result(self.fcoin_obj.create_order(**params),self.__common_print_func)

if __name__ == '__main__':
    FcmdObj().cmdloop()
