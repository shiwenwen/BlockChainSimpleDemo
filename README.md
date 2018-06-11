基于Python3区块链简单Demo，帮助了解区块链。
---
> ***今年早些时候区块链可谓是火热到不行，不管是技术人员还是非技术人员，都知道这样一项改革性的技术。介绍区块链的文章书籍颇多，但是实践才会让你更好的理解，这篇文章将用Python3来创建一个简单的区块链来演示区块链到底是如何工作的。***

本文将分为四个部分：

- 创建一个基本的区块链
- 实现共识算法（本文采用POW工作量证明）
- 实现交易和挖矿奖励

# 1. 创建基本的区块链
> 区块链简单来说实际上是一个去中心化的由一个个数据区块链接在一起的公共数据库，数据区块在添加到区块链后，是不会再被改变的，这依赖于区块链的共识机制。当然万事都不可能是绝对的，例如在POW下，如果有用全网一半以上的算力，是有可能改变链上的数据的，但是达到这种条件并作出数据改变所带来的利益是赶不上你付出的代价的。

## 1.1 创建一个区块
-  ***首先我们创建一个区块类，代表区块链上的每一个区块，新建`Block.py`***

```python
import hashlib


class Block:

    def __init__(self, timestamp, data, previous_hash=''):
        '''
        区块的初始化
        :param timestamp: 创建时的时间戳
        :param data: 区块数据
        :param previous_hash: 上一个区块的hash
       :param hash: 区块的hash
        '''
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        '''
        计算区块哈希值
        :return:
        '''
        # 将区块信息拼接然后生成sha256的hash值
        raw_str = self.previous_hash + str(self.timestamp) + json.dumps(self.data, ensure_ascii=False)
        sha256 = hashlib.sha256()
        sha256.update(raw_str.encode('utf-8'))
        hash = sha256.hexdigest()
        return hash


```
引入`hashlib`模块用于计算hash值，是Block的`__init__`方法中我们对区块进行了基本的初始化，每个区块都包含着上个区块的hash值，用于校验数据完整。`data`保存着此区块的数据，如果是加密货币，如比特币，那这个data就是交易的事务。`calculate_hash`方法用于计算当前区块的hash值。
<table><tr><td bgcolor=#0096ff  > <font color=white>Tip：Hash算法简单来说就是一种将任意长度的消息压缩到某一固定长度的消息摘要的函数。sha256是SHA密码散列函数家族中的一种Hash算法，不同的输入的散列刷出都是不同的，输入的一点改动都会导致hash值的完全不同。所以hash算法可用来校验数据是否改动。</font></td></tr></table>

## 1.2 创建一个链
- ***创建一个区块链，新建`BlockChain.py`***

```python
from Block import Block
import time


class BlockChain:
    def __init__(self):
        # 初始化链，添加创世区块
        self.chain = [self._create_genesis_block()]

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

    def add_block(self, block):
        '''
        添加区块
        :param block: 要添加的区块
        :return:
        '''
        block.previous_hash = self.get_latest_block().hash
        block.hash = block.calculate_hash()
        self.chain.append(block)

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
    # 测试使用区块链
    blockChain = BlockChain()
    # 添加区块
    blockChain.add_block(Block(time.time(), {'amount': 100}))
    blockChain.add_block(Block(time.time(), {'amount': 200}))
    # 检查区块链有效性 有效
    print('区块链是否有效? ', '有效' if blockChain.verify_blockchain() else '无效')
    # 尝试修改区块数据
    blockChain.chain[1].data = {'amount': 10}
    # 检查区块链有效性 无效
    print('区块链是否有效? ', '有效' if blockChain.verify_blockchain() else '无效')


```
  在区块链初始化的时候我们创建了一个创世区块并添加到链上（这里我们用的是一个数组），创建好区块链后，我们给区块链上增加了两个区块，然后校验区块链的有有效性，运行结果是有效的，随后我们改动了一个区块的数据，再次校验的结果就是无效了。

---

## 2. 实现共识算法  POW

> 我们已经创建好一个区块链了，但是这个区块链并不完整，有着很多问题：
 - 人们可以快速的创建任何区块添加到区块链中，这会导致我们的区块链充满着垃圾数据导致区块链过载而无法正常使用
 - 创建区块过于容易，所以我们可以不需要多大的算力和代价，就可以轻易的篡改数据并重新计算所有的Hash值使我们的篡改有效。

> 所以我们需要共识机制来解决这样的问题，这里我们介绍比特币使用的***POW***工作量证明。

### 2.1 什么是POW
POW是一种共识机制，通过一定量的的复杂的耗时运算获取到指定的结果，并且这个结果能迅速的被验证。以耗用的时间、设备与能源做为担保成本，从而防止数据滥用。
***因为Hash散列的输入稍有变动，就会生成完全不一样的散列值，所以几乎无法通过hash值推导出原来的数据，我们让区块链的节点通过大量的穷举运算找到指定值从而实现POW。***
比特币通过要求hash以特定0的数目来实现POW。这也被称之为难度。那我们如何改变区块的hash值呢，因为区块的创建时间和区块所包含的数据是不希望被改变的，所以我们需要引入一个新的值，通过这个值的变化来改变区块的hash值

我们给区块添加一个`nonce`值。`nonce`是用来查找一个有效hash的次数。由于无法预测hash函数的输出，因此在获得满足难度条件的hash之前，我们只能通过大量的尝试来找个一个有效的hash值创建一个新的区块，这就是所谓的挖矿。
比特币规定每10分钟只能添加一个区块。可以想象创建一个区块需要多大的算力，要想篡改区块几乎是不可能的。

### 2.2 实现POW
- 首先我们给Block类增加`nonce`随机数属性，并初始化为`0`。

```python

    def __init__(self, timestamp, data, previous_hash=''):
        '''
        区块的初始化
        :param timestamp: 创建时的时间戳
        :param data: 区块数据
        :param previous_hash: 上一个区块的hash
        :param hash: 区块的hash
        '''
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.nonce = 0
		self.hash = self.calculate_hash()

```
- 然后我们修改`calculate_hash`方法，在计算hash值时包含nonce。

```python

    def calculate_hash(self):
        '''
        计算区块哈希值
        :return:
        '''
        # 将区块信息拼接然后生成sha256的hash值
        raw_str = self.previous_hash + str(self.timestamp) + json.dumps(self.data, ensure_ascii=False) + str(self.nonce)
        sha256 = hashlib.sha256()
        sha256.update(raw_str.encode('utf-8'))
        hash = sha256.hexdigest()
        return hash

```
- 实现挖矿的方法
```python

    def mine_block(self, difficulty):
        '''
        挖矿
        :param difficulty: 难度
        :return:
        '''
        time_start = time.clock()
        # 要求hash值前difficulty个位为0
        while self.hash[0: difficulty] != ''.join(['0'] * difficulty):
            # 符合要求
            self.nonce += 1
            self.hash = self.calculate_hash()
        print("挖到区块:%s, 耗时: %f秒" % (self.hash, time.clock() - time_start))
```
### 2.3 修改区块链
- 我们给BlockChain类增加一个`difficulty`难度属性，初始难度我们设置为5，这意味着区块的hash必须以5个0开头，当然这个难度你是可以自己调整的，难度越大挖矿需要的时间越久。

```python
    def __init__(self):
        # 初始化链，添加创世区块
        self.chain = [self._create_genesis_block()]
        # 设置初始难度
        self.difficulty = 5
```
- 然后我们修改`add_block`方法，确保区块被挖到

```python
    def add_block(self, block):
        '''
        添加区块
        :param block: 要添加的区块
        :return:
        '''
        block.previous_hash = self.get_latest_block().hash
        # 开始挖矿
        block.mine_block(self.difficulty)
        # 挖矿结束后添加到链上
        self.chain.append(block)

```
- 测试

```python
    blockChain = BlockChain()
    blockChain.add_block(Block(time.time(), {'amount': 100}))
    blockChain.add_block(Block(time.time(), {'amount': 200}))
```
运行结果
![](https://sww-wordpress.oss-cn-beijing.aliyuncs.com/2018/06/mine-block-time.png)
**到此我们的区块链的雏形就完成了，但这也并不是一个完整的区块链，它没有运行在P2P网络上，也缺少很多功能，这里只是为了说明区块链的工作原理。**

---
## 3. 实现交易与挖矿奖励
> 现在我将要把我们的区块链变成电子货币，在区块中存储交易数据，并且挖矿是给予矿工一定奖励以激励矿工挖矿保持区块链的运转

### 3.1 添加交易类
***新建文件Transaction.py,我们使用交易类来保存每一笔交易信息***

```python
class Transaction():
    def __init__(self, from_address, to_address, amount):
        '''
        初始化交易
        :param from_address: 交易发起方 
        :param to_address: 交易接收方
        :param amount: 交易金额
        '''
        self.from_address = from_address
        self.from_address = to_address
        self.amount = amount
```
这里为了能把交易类转成json字符串，方便传输和使用。我们实现`TransactionEncoder`类继承自`json.JSONEncoder`

```python
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


```
### 3.2 调整区块链代码
- 一个区块应该包含多笔交易，在一个新的区块被开采出来之前，是可以提交新的交易的，所以我们需要存储待处理的交易

```python
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
```
- 我们给`BlockChain`增加了一个`pending_transactions`属性用于存储待处理的交易，同时添加了一个`mining_reward`作为挖矿奖励。
然后我们把`add_block`方法去掉，换成更符合情景的`add_transaction`：

```python

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

```
- 现在我们`Block`中的data属性保存的就是挖矿的待处理交易数据，所以我们来修改一下这个属性名，改为`transactions`让其符合请情景。
所以我们的`Block`应该是现在这个样子:

```python
import hashlib
import json
import time
from Transaction import TransactionEncoder


class Block:

    def __init__(self, timestamp, transactions, previous_hash=''):
        '''
        区块的初始化
        :param timestamp: 创建时的时间戳
        :param transactions: 区块数据
        :param previous_hash: 上一个区块的hash
        :param hash: 区块的hash
        '''
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.transactions = transactions
        self.nonce = 0
        self.hash = self.calculate_hash()


    def calculate_hash(self):
        '''
        计算区块哈希值
        :return:
        '''
        # 将区块信息拼接然后生成sha256的hash值
        raw_str = self.previous_hash + str(self.timestamp) + json.dumps(self.transactions, ensure_ascii=False, cls=TransactionEncoder) + str(self.nonce)
        sha256 = hashlib.sha256()
        sha256.update(raw_str.encode('utf-8'))
        hash = sha256.hexdigest()
        return hash

    def mine_block(self, difficulty):
        '''
        挖矿
        :param difficulty: 难度
        :return:
        '''
        time_start = time.clock()
        # 要求hash值前difficulty个位为0
        while self.hash[0: difficulty] != ''.join(['0'] * difficulty):
            # 符合要求
            self.nonce += 1
            self.hash = self.calculate_hash()
        print("挖到区块:%s, 耗时: %f秒" % (self.hash, time.clock() - time_start))


```
- 我们在将交易转成为json字符串的时候，使用了` cls=TransactionEncoder`指定了编码器,因为`Transaction`是我们自己写的类，所以`json.dumps`无法进行编码。

- 然后我们给`BlockChain`添加一个挖取待处理交易的方法``，有了交易，那我们应该可以查看我们账户上的余额，所以我们再添加一个查看钱包余额的方法``：
```python
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
```
***可以看出，谁挖矿成功后，就会在待处理交易中产生一笔新交易，包含着自己挖矿的奖励，所以我们的奖励并不是实时到账的，在下一次挖矿成功后，我们的此次挖矿奖励才会真正的到我们的账户上。***

### 3.3 测试

```python
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
```
运行结果：
![](https://sww-wordpress.oss-cn-beijing.aliyuncs.com/2018/06/blockchain-mine-balance.png)

---
> **到此，我们的交易就完成了，但是还是有多没有完善的东西，例如添加交易的时候没有校验账户金额是否可以完成交易，没有创建钱包和交易签名等等。但是我们的目了解区块链的的已经达到了！**
