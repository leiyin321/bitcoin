#!/usr/bin/python
# -- coding:utf-8 --

import json
import time
import urllib2

from redis import Redis
import oksdk

api_key = ''
secretkey = ''

redis=Redis('127.0.0.1',6379,1)

def place_order(symbol,price,amount,typ):
    print 'place_order',symbol,price,amount,typ
    param={
        'contract_type':'quarter',# 合约类型: this_week:当周   next_week:下周   quarter:季度
        'match_price':'0',
        'lever_rate':'20',
        'symbol': symbol,
        'price': str(price),
        'amount': str(amount),
        'type': typ,# 1:开多   2:开空   3:平多   4:平空
    }
    order_info = oksdk.post('www.okex.com','/api/v1/future_trade.do?',param,api_key,secretkey)
    print order_info
    return [price,order_info['order_id']]

def place_orders(orders):
    print 'place_orders',json.dumps(orders)
    param = {
        'symbol':'btc_usd',
        'contract_type':'quarter',
        'lever_rate':'20',
        'orders_data':json.dumps(orders).replace(' ',''),
    }
    orders_info = oksdk.post('www.okex.com','/api/v1/future_batch_trade.do?',param,api_key,secretkey)
    print json.dumps(orders_info)
    return orders_info

def future_order_info(order_id):
    print 'future_order_info',order_id
    param = {
        'symbol': 'btc_usd',
        'contract_type': 'quarter',
        'order_id': order_id,
    }
    order_info = oksdk.post('www.okex.com','/api/v1/future_order_info?',param,api_key,secretkey)
    #print json.dumps(order_info)
    return order_info['orders'][0]

class net:
    def __init__(self,window,step,amount,mid):
        self.window = window
        self.step = step
        self.amount = amount
        # init buy_list
        if redis.llen('buy_list')==0:
            price = mid-window/2
            orders = []
            for i in xrange(100):
                order = {
                    'price':str(price),
                    'amount':str(amount),
                    'type':'1',
                    'match_price':'0',
                }
                orders.append(order)
                #order_info = place_order('btc_usd',price,amount,'1')
                #redis.rpush('buy_list',json.dumps(order_info))
                price -= step
                #time.sleep(0.2)
            for i in xrange(20):
                bat_orders = orders[i*5:i*5+5]
                order_infos = place_orders(bat_orders)['order_info']
                for index in xrange(5):
                    order_info = [float(bat_orders[index]['price']),order_infos[index]['order_id']]
                    redis.rpush('buy_list',json.dumps(order_info))
                time.sleep(0.2)
        # init sell_list
        if redis.llen('sell_list')==0:
            price = mid+window/2
            orders = []
            for i in xrange(100):
                order = {
                    'price':str(price),
                    'amount':str(amount),
                    'type':'2',
                    'match_price':'0',
                }
                orders.append(order)
                #order_info = place_order('btc_usd',price,amount,'2')
                #redis.rpush('sell_list',json.dumps(order_info))
                price += step
                #time.sleep(0.2)
            for i in xrange(20):
                bat_orders = orders[i*5:i*5+5]
                order_infos = place_orders(bat_orders)['order_info']
                for index in xrange(5):
                    order_info = [float(bat_orders[index]['price']),order_infos[index]['order_id']]
                    redis.rpush('sell_list',json.dumps(order_info))
                time.sleep(0.2)

    def check_buy_list(self):
        while redis.lindex('buy_list',0):
            time.sleep(0.2)
            order_info = json.loads(redis.lindex('buy_list',0))
            order_status = future_order_info(order_info[1])
            if order_status['status'] == 2: #全部成交
                redis.lpop('buy_list')
                if order_status['type'] == 1: #开多
                    order_info1 = place_order('btc_usd',order_info[0]+self.window,self.amount,'3') #平多
                    if redis.llen('buy_list') == 0:
                        time.sleep(0.2)
                        order_info2 = place_order('btc_usd',order_info[0]-self.window,self.amount,'1') #开多
                        redis.lpush('buy_list',json.dumps(order_info2))
                elif order_status['type'] == 4: #平空
                    order_info1 = place_order('btc_usd',order_info[0]+self.window,self.amount,'2') #开空
                redis.lpush('sell_list',json.dumps(order_info1))
            else:
                break

    def check_sell_list(self):
        while redis.lindex('sell_list',0):
            time.sleep(0.2)
            order_info = json.loads(redis.lindex('sell_list',0))
            order_status = future_order_info(order_info[1])
            if order_status['status'] == 2: #全部成交
                redis.lpop('sell_list')
                if order_status['type'] == 2: #开空
                    order_info1 = place_order('btc_usd',order_info[0]-self.window,self.amount,'4') #平空
                    if redis.llen('sell_list') == 0:
                        time.sleep(0.2)
                        order_info2 = place_order('btc_usd',order_info[0]+self.window,self.amount,'2') #开空
                        redis.lpush('sell_list',json.dumps(order_info2))
                elif order_status['type'] == 3: #平多
                    order_info1 = place_order('btc_usd',order_info[0]-self.window,self.amount,'1') #开多
                redis.lpush('buy_list',json.dumps(order_info1))
            else:
                break

    def run(self):
        while True:
            self.check_buy_list()
            self.check_sell_list()

def get_latest_price():
    trade = oksdk.get('https://www.okex.com/api/v1/future_trades.do?symbol=btc_usd&contract_type=quarter')
    return trade[0]['price']

if __name__ == '__main__':
    mid = get_latest_price()
    print mid
    my_net = net(8,8,20,mid)
    my_net.run()
