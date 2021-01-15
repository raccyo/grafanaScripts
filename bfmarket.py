# -*- coding: utf-8 -*-
#!/usr/bin/python3
import datetime
import json
import websocket
import dateutil.parser
import time
from threading import Thread
import signal
import os
from influxdb import InfluxDBClient

latency_min_fx = 10000
latency_max_fx = -10000
ltp_fx = 0
latency_min_spot = 10000
latency_max_spot = -10000
ltp_spot = 0


def quit_loop(signal, frame):
    os._exit(0)


class Websocketexecutions(object):
    def __init__(self, url):
        self._url = url
        self._channel_executions_fx = "lightning_executions_FX_BTC_JPY"
        self._channel_executions_spot = "lightning_executions_BTC_JPY"

    def startWebsocket(self):
        def format_date(date_line):
            exec_date = date_line.replace('T', ' ')[:-1]
            return datetime.datetime(int(exec_date[0:4]), int(exec_date[5:7]), int(exec_date[8:10]),
                                     int(exec_date[11:13]), int(exec_date[14:16]), int(exec_date[17:19]), int(exec_date[20:26]),
                                     ) + datetime.timedelta(hours=9) if len(exec_date) == 27 else dateutil.parser.parse(exec_date) + datetime.timedelta(hours=9)

        def on_open(ws):
            print("Websocket connected")
            ws.send(json.dumps({"method": "subscribe", "params": {
                    "channel": self._channel_executions_fx}}))
            ws.send(json.dumps({"method": "subscribe", "params": {
                    "channel": self._channel_executions_spot}}))

        def on_error(ws, error):
            print(error)

        def on_close(ws):
            print("Websocket closed")

        def run(ws):
            while True:
                ws.run_forever()
                time.sleep(3)

        def on_message(ws, message):
            global latency_min_fx,   latency_max_fx,   ltp_fx
            global latency_min_spot, latency_max_spot, ltp_spot

            messages = json.loads(message)
            params = messages["params"]
            channel = params["channel"]
            recept_data = params["message"]

            currenttime = time.time()
            f = recept_data[-1]
            exec_date = format_date(f["exec_date"])
            latency = round(currenttime-exec_date.timestamp(), 3)

            if channel == self._channel_executions_fx:
                ltp_fx = f["price"]
                latency_min_fx = min(latency_min_fx, latency)
                latency_max_fx = max(latency_max_fx, latency)

            if channel == self._channel_executions_spot:
                ltp_spot = f["price"]
                latency_min_spot = min(latency_min_spot, latency)
                latency_max_spot = max(latency_max_spot, latency)

        ws = websocket.WebSocketApp(
            self._url, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
        websocketThread = Thread(target=run, args=(ws, ))
        websocketThread.start()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, quit_loop)

    client = InfluxDBClient(host='localhost', port=8086, database='bots')

    ws = Websocketexecutions(url='wss://ws.lightstream.bitflyer.com/json-rpc')
    ws.startWebsocket()

    while True:
        time.sleep(1)
        # 10秒毎にInfluxDBへ登録
        if time.time() % 10 < 1:
            if latency_min_fx != 10000:
                try:
                    data = [{"measurement": "bf_market", "fields": {'ltp_fx': float(
                        ltp_fx), 'latency_min_fx': float(latency_min_fx), 'latency_max_fx': float(latency_max_fx), }}]
                    client.write_points(data)
                except:
                    pass
            latency_min_fx = 10000
            latency_max_fx = -10000

            if latency_min_spot != 10000:
                try:
                    data = [{"measurement": "bf_market", "fields": {'ltp_spot': float(ltp_spot), 'latency_min_spot': float(
                        latency_min_spot), 'latency_max_spot': float(latency_max_spot), }}]
                    client.write_points(data)
                except:
                    pass
            latency_min_spot = 10000
            latency_max_spot = -10000
