# coding=utf-8

class Strategy(object):

    def __init__(self):
        pass

    def reform_data(self, jo):
        return jo

    def init_strategy_data(self):
        pass

    def generate_excmd_from_feeder_data(self, data):
        return []

    def update_status_from_exeback(self, order_result):
        return True

    def clean_excmd(self):
        return []

    def init_excmd(self):
        return []