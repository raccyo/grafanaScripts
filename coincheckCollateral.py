# -*- coding: utf-8 -*-
#!/usr/bin/python3
import time
from datetime import datetime
import yaml
from influxdb import InfluxDBClient
import requests
import hmac
import hashlib
import json

ENDPOINT = 'https://coincheck.com'


def get_signature(message):
    return hmac.new(
        bytes(secret.encode('ascii')),
        bytes(message.encode('ascii')),
        hashlib.sha256
    ).hexdigest()

def get_nance():
    return str(int(time.time())-80000)

def get_headers(nonce, signature):
    return {
        'ACCESS-KEY': key,
        'ACCESS-NONCE': nonce,
        'ACCESS-SIGNATURE': signature,
        'Content-Type': 'application/json'
    }

def get(path, params=None):
    if params != None:
        params = json.dumps(params)
    else:
        params = ''
    nonce = get_nance()
    message = nonce + ENDPOINT + path + params

    signature = get_signature(message)

    return requests.get(
        ENDPOINT+path+params,
        headers=get_headers(nonce, signature)
    ).json()

def balance():
    return get('/api/accounts/balance')

def ticker():
    return get('/api/ticker')

if __name__ == '__main__':
    f = open('key.yaml', 'r+')
    data = yaml.load(f, Loader=yaml.FullLoader)
    key = data['coincheck_key']
    secret = data['coincheck_secret']
    ltp = 0
    client = InfluxDBClient(host='localhost', port=8086, database='bots')
    while True:
        try:
            print(ticker())
            ltp = int(ticker()['last'])
            time.sleep(5)
            balance_dict = balance()
            collateral = float(balance_dict['jpy']) + float(balance_dict['btc']) * ltp
            print(collateral)
            data = [{"measurement": "coincheck_collateral", "fields": {
                'coincheck_collateral': int(collateral)}}]
            client.write_points(data)
        except:
            import traceback
            traceback.print_exc()
            pass
        time.sleep(50)
