# -*- coding: utf-8 -*-
#!/usr/bin/python3
import time
from threading import Thread
import yaml
from influxdb import InfluxDBClient
import ccxt
import requests

if __name__ == '__main__':
    f=open('key.yaml','r+')
    data = yaml.load(f, Loader=yaml.FullLoader)
    key=data['bybit_key']
    secret=data['bybit_secret']
    bybit = ccxt.bybit()
    bybit.apiKey = key
    bybit.secret = secret
    client = InfluxDBClient(host='localhost', port=8086, database='bots')
    while True:
        try:
          res = bybit.fetch_balance()
          pos = bybit.privateGetPositionList({'symbol': 'BTCUSD'})
          balance_btc = float(res['BTC']['free']) + float(res['BTC']
                                                          ['used']) + float(pos['result']['unrealised_pnl'])
          last = bybit.fetch_ticker('BTC/USD')['last']
          balance_usd = balance_btc*last
          res = requests.get(url="https://api.exchangeratesapi.io/latest").json()
          usd_jpy = res['rates']['JPY']/res['rates']['USD']
          balance_jpy = balance_usd * usd_jpy
          data = [{"measurement": "bybit_collateral", "fields": {
              'bybit_collateral': int(balance_jpy)}}]
          client.write_points(data)
        except:
          pass
        time.sleep(60)
