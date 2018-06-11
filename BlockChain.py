# -*- coding:utf-8 -*-
# Author: ShiWenWen
from Block import Block
import time
from Transaction import Transaction


class BlockChain:
    def __init__(self):
        # 初始化链，添加创世区块
        self.chain = [self._create_genesis_block()]
        # 设置初始难度
        self.difficulty = 5
        # 待处理交易
        self.pending_transactions = []
        # 设置一个挖矿奖励
        self.mining_reward = 100

    @staticmethod
    def _create_genesis_block():
        '''
        生成创世区块
        :return: 创世区块
        '''
        timestamp = time.mktime(time.strptime('2018-06-11 00:00:00', '%Y-%m-%d %H:%M:%S'))
        block = Block(timestamp, [], '')
        return block

    def get_latest_block(self):
        '''
        获取链上最后一个也是最新的一个区块
        :return:最后一个区块
        '''
        return self.chain[-1]

    # def add_block(self, block):
    #     '''
    #     添加区块
    #     :param block: 要添加的区块
    #     :return:
    #     '''
    #     block.previous_hash = self.get_latest_block().hash
    #     # 开始挖矿
    #     block.mine_block(self.difficulty)
    #     # 挖矿结束后添加到链上
    #     self.chain.append(block)

    def add_transaction(self, transaction):
        '''
        添加交易
        :param transaction: 新交易
        :return:
        '''
        # 这里应该根据业务对交易进行一些列的验证
        '''...'''
        # 添加到待处理交易
        self.pending_transactions.append(transaction)

    def mine_pending_transaction(self, mining_reward_address):
        '''
        挖取待处理交易
        :param mining_reward_address: 挖矿奖励的地址
        :return:
        '''
        block = Block(time.time(), self.pending_transactions, self.chain[-1].hash)
        block.mine_block(self.difficulty)
        self.chain.append(block)
        # 挖矿成功后 重置待处理事务 添加一笔事务 就是此次挖矿的奖励
        self.pending_transactions = [
            Transaction(None, mining_reward_address, self.mining_reward)
        ]

    def get_balance_of_address(self, address):
        '''
        获取钱余额
        :param address: 钱包地址
        :return: 余额
        '''
        balance = 0
        for block in self.chain:
            for trans in block.transactions:
                if trans.from_address == address:
                    # 自己发起的交易 支出
                    balance -= trans.amount
                if trans.to_address == address:
                    # 收入
                    balance += trans.amount
        return balance

    def verify_blockchain(self):
        '''
        校验区块链数据是否完整 是否被篡改过
        :return: 校验结果
        '''
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]  # 当前遍历到的区块
            previous_block = self.chain[i - 1]  # 当前区块的上一个区块
            if current_block.hash != current_block.calculate_hash():
                # 如果当前区块的hash值不等于计算出的hash值，说明数据有变动
                return False
            if current_block.previous_hash != previous_block.calculate_hash():
                # 如果当前区块记录的上个区块的hash值不等于计算出的上个区块的hash值 说明上个区块数据有变动或者本区块记录的上个区块的hash值被改动
                return False
        return True


if __name__ == '__main__':
    blockChain = BlockChain()
    # 添加两笔交易
    blockChain.add_transaction(Transaction('address1', 'address2', 100))
    blockChain.add_transaction(Transaction('address2', 'address1', 50))
    # address3 挖取待处理的交易
    blockChain.mine_pending_transaction('address3')
    # 查看账户余额
    print('address1 余额 ', blockChain.get_balance_of_address('address1'))
    print('address2 余额 ', blockChain.get_balance_of_address('address2'))
    print('address3 余额 ', blockChain.get_balance_of_address('address3'))
    # address2 挖取待处理的交易
    blockChain.mine_pending_transaction('address2')
    print('address1 余额 ', blockChain.get_balance_of_address('address1'))
    print('address2 余额 ', blockChain.get_balance_of_address('address2'))
    print('address3 余额 ', blockChain.get_balance_of_address('address3'))

