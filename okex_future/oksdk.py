#!/usr/bin/python
# -- coding:utf-8 --

import httplib
import json
import urllib2
import urllib
import hashlib
import time

TIMEOUT = 5
headers = {
'Content-type':'application/x-www-form-urlencoded',
'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
}

def buildMySign(params,secretKey):
    sign = ''
    sign = '&'.join(['%s=%s'%(k,v) for k,v in sorted(params.items())])
    #print sign
    return  hashlib.md5((sign+'&secret_key='+secretKey).encode("utf-8")).hexdigest().upper()

def get(url):
    req = urllib2.Request(url,headers=headers)
    resp = urllib2.urlopen(req, timeout=TIMEOUT)
    return json.loads(resp.read())

def post(host,url,params,api_key,secretkey):
    params['api_key']=api_key
    sign = buildMySign(params,secretkey)
    params['sign']=sign
    params = urllib.urlencode(params)
    #print host,url,params
    conn = httplib.HTTPSConnection(host,timeout=TIMEOUT)
    conn.request("POST", url, params, headers)
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    conn.close()
    return json.loads(data)

class client:
    def __init__(self,api_key,secretkey):
        self.api_key = api_key
        self.secretkey = secretkey
    def userinfo(self):
        url = '/api/v1/future_userinfo.do?'
        return post('www.okex.com',url,{},self.api_key,self.secretkey)


if __name__ == '__main__':
    api_key = ''
    secretkey = ''
    c = client(api_key,secretkey)
    print c.userinfo()


