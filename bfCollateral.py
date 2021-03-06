# -*- coding: utf-8 -*-
#!/usr/bin/python3
import time
from threading import Thread
import pybitflyer
import yaml
from influxdb import InfluxDBClient

if __name__ == '__main__':
    f=open('key.yaml','r+')
    data = yaml.load(f, Loader=yaml.FullLoader)
    key=data['bf_key']
    secret=data['bf_secret']
    api = pybitflyer.API(api_key=key, api_secret=secret)
    client = InfluxDBClient(host='localhost', port=8086, database='bots')
    while True:
        try:
          res = api.getcollateral()
          bf_collateral = float(res['collateral']) + float(res['open_position_pnl'])
          data = [{"measurement": "bf_collateral", "fields": {'bf_collateral': int(bf_collateral)}}]
          client.write_points(data)
        except:
          pass
        time.sleep(60)
