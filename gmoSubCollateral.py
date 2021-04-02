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

ENDPOINT = 'https://api.coin.z.com/private'

def get_headers(path, method, body=''):
    timestamp = '{0}000'.format(
        int(time.mktime(datetime.now().timetuple())))
    text = ''.join([timestamp, method, path])
    if method == 'POST':
        text = ''.join([timestamp, method, path, json.dumps(body)])
    sign = get_sign(text)
    return {
        "API-KEY": key,
        "API-TIMESTAMP": timestamp,
        "API-SIGN": sign
    }

def get_sign(text):
    sign = hmac.new(
        bytes(
            secret.encode('ascii')), bytes(
            text.encode('ascii')), hashlib.sha256).hexdigest()
    return sign


def get_margin():
    path = '/v1/account/margin'
    method = 'GET'
    headers = get_headers(path, method)
    res = requests.get(ENDPOINT+path, headers=headers).json()
    return res


if __name__ == '__main__':
    f = open('key.yaml', 'r+')
    data = yaml.load(f, Loader=yaml.FullLoader)
    key = data['gmo_sub_key']
    secret = data['gmo_sub_secret']
    client = InfluxDBClient(host='localhost', port=8086, database='bots')
    while True:
        try:
            margin = get_margin()['data']['actualProfitLoss']
            data = [{"measurement": "gmo_sub_collateral", "fields": {
                'gmo_sub_collateral': int(margin)}}]
            client.write_points(data)
        except:
            import traceback
            traceback.print_exc()
            pass
        time.sleep(60)
