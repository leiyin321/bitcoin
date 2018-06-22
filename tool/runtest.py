#!/usr/local/bin/env python
# -- coding:utf-8 --

import json
import urllib2

huobipro_kline_url = 'https://api.huobipro.com/market/history/kline?symbol=%s&period=%s&size=%s'

def get_kline(url):
    try:
	kline = json.loads(urllib2.urlopen(url).read())['data']
	return kline
    except Exception,e:
	print 'get kline error: ',str(e)
	return []

def get_signs(kline):
    signs=[]
    for period in kline:
	if period['open'] < period['close']:
	    signs.append(1)
	elif period['open'] > period['close']:
	    signs.append(-1)
	elif period['open'] == period['close']:
	    signs.append(0)
    #signs = [1,-1,-1,-1,1,1,1,0,1,1,-1,-1,-1,1,0,-1,1,-1,0,1]
    print signs
    return signs

def run_test(symbol='btcusdt',period='1min',size='100'):
    kline = get_kline(huobipro_kline_url%(symbol,period,size))
    signs = get_signs(kline)
    u=0;n1=0;n2=0
    last = 0
    for sign in signs:
	if sign == 0:
	    last = sign
	    continue
	if sign == 1: n1+=1
	if sign == -1: n2+=1
	if sign != last: u+=1
	last = sign
    x_ = 2.0*n1*n2/(n1+n2) + 1
    s = (2.0*n1*n2*(2.0*n1*n2-n1-n2)/((n1+n2)**2)/(n1+n2-1))**0.5
    Z = (abs(u-x_)-0.5)/s
    print 'u:%d n1:%d n2:%d'%(u,n1,n2)
    print 'x_:%f s:%f Z:%f'%(x_,s,Z)
    return Z


if __name__ == '__main__':
    run_test('btcusdt','1min','1000')
	
	

