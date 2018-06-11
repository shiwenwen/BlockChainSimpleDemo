# -*- coding:utf-8 -*-
# Author: ShiWenWen
import json


class Transaction:
    def __init__(self, from_address, to_address, amount):
        '''
        初始化交易
        :param from_address: 交易发起方
        :param to_address: 交易接收方
        :param amount: 交易金额
        '''
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount


class TransactionEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Transaction):
            return o.__dict__
        return json.JSONEncoder.default(self, o)


if __name__ == '__main__':
    # 测试
    tran = Transaction('aaa', 'bbb', 100)
    print(tran)
    print(json.dumps(tran, ensure_ascii=False, cls=TransactionEncoder))


