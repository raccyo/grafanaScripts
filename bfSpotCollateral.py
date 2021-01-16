# -*- coding: utf-8 -*-
#!/usr/bin/python3
import time
from threading import Thread
import pybitflyer
import yaml
from influxdb import InfluxDBClient
import json
import websocket
import signal
import os

def quit_loop(signal, frame):
    os._exit(0)

class Websocketexecutions(object):
    def __init__(self, channel):
        self._url = 'wss://ws.lightstream.bitflyer.com/json-rpc'
        self._channel_executions = channel
        self.ltp = 0

    def startWebsocket(self):
        def on_open(ws):
            print("Websocket connected")
            ws.send(json.dumps({"method": "subscribe", "params": {
                    "channel": self._channel_executions}}))

        def on_error(ws, error):
            print(error)

        def on_close(ws):
            print("Websocket closed")

        def run(ws):
            while True:
                ws.run_forever()
                time.sleep(3)

        def on_message(ws, message):
            messages = json.loads(message)
            params = messages["params"]
            recept_data = params["message"]
            self.ltp = recept_data[-1]["price"]

        ws = websocket.WebSocketApp(
            self._url, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
        websocketThread = Thread(target=run, args=(ws, ))
        websocketThread.start()
      
if __name__ == '__main__':
    signal.signal(signal.SIGINT, quit_loop)
    ws_btc_jpy = Websocketexecutions(channel="lightning_executions_BTC_JPY")
    ws_btc_jpy.startWebsocket()
    ws_eth_jpy = Websocketexecutions(channel="lightning_executions_ETH_JPY")
    ws_eth_jpy.startWebsocket()
    f=open('key.yaml','r+')
    data = yaml.load(f, Loader=yaml.FullLoader)
    key=data['bf_key']
    secret=data['bf_secret']
    api = pybitflyer.API(api_key=key, api_secret=secret)
    client = InfluxDBClient(host='localhost', port=8086, database='bots')
    time.sleep(5)
    while True:        
        try:
          balance = api.getbalance()
          for a in balance:
            if a['currency_code'] == 'BTC':
              bf_btc = a['amount']
            elif a['currency_code'] == 'ETH':
              bf_eth = a['amount']
            elif a['currency_code'] == 'JPY':
              bf_jpy = a['amount']
          bf_btc_jpy = bf_btc * ws_btc_jpy.ltp
          bf_eth_jpy = bf_eth * ws_eth_jpy.ltp
          bf_jpy += bf_btc_jpy + bf_eth_jpy
          data = [{"measurement": "bf_SpotCollateral", "fields": {'bf_SpotCollateral': int(bf_jpy)}}]
          client.write_points(data)
        except:
          pass
        time.sleep(60)
