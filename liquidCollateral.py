from quoine.client import Quoinex
import yaml
import traceback
import time
from influxdb import InfluxDBClient

class Liquid(Quoinex):
    API_URL = 'https://api.liquid.com'


if __name__ == '__main__':
    f = open('key.yaml', 'r+')
    data = yaml.load(f, Loader=yaml.FullLoader)
    key = data['liquid_key']
    secret = data['liquid_secret']
    liquid = Liquid(key, secret)
    client = InfluxDBClient(host='localhost', port=8086, database='bots')
    while True:
        try:
            margin = liquid.get_trading_accounts()[0]['equity']
            data = [{'measurement':"liquid_collateral", "fields":{
                "liquid_collateral": float(margin)
            }}]
            client.write_points(data)
        except:
            traceback.print_exc()
        time.sleep(60)
