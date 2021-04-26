# -*- coding: utf-8 -*-
#!/usr/bin/python3
import time
from threading import Thread
import yaml
from influxdb import InfluxDBClient
import ccxt
import requests
symbols = [{'symbol': 'BTCUSD', 'crypt': 'BTC', 'slash': 'BTC/USD'},
           {'symbol': 'ETHUSD', 'crypt': 'ETH', 'slash': 'ETH/USD'}]


def getMid(symbol, items):
    values = [(float(x['ask']) + float(x['bid'])) / 2
              for x in items if 'currencyPairCode' in x and 'ask' in x and 'bid' in x and x['currencyPairCode'] == symbol]
    return values[0] if values else None


if __name__ == '__main__':
    f = open('key.yaml', 'r+')
    data = yaml.load(f, Loader=yaml.FullLoader)
    key = data['bybit_key']
    secret = data['bybit_secret']
    bybit = ccxt.bybit()
    bybit.apiKey = key
    bybit.secret = secret
    client = InfluxDBClient(host='localhost', port=8086, database='bots')
    while True:
        try:
            res = bybit.fetch_balance()
            balance_usd = 0
            for symbol in symbols:
                pos = bybit.privateGetPositionList(
                    {'symbol': symbol['symbol']})
                balance = float(res[symbol['crypt']]['free']) + float(
                    res[symbol['crypt']]['used']) + float(pos['result']['unrealised_pnl'])
                last = bybit.fetch_ticker(symbol['slash'])['last']
                balance_usd += balance * last
            print(res['total']['BTC'])
            trade = requests.get(
                url="https://www.gaitameonline.com/rateaj/getrate").json()
            usd_jpy = getMid('USDJPY', trade['quotes'])
            balance_jpy = balance_usd * usd_jpy
            data = [{"measurement": "bybit_collateral", 
            "fields": {
                'bybit_collateral': int(balance_jpy),
                'bybit_btc': float(res['total']['BTC'])
                }}]
            client.write_points(data)
        except BaseException:
            import traceback
            traceback.print_exc()
            pass
        time.sleep(60)
