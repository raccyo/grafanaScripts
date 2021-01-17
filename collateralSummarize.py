from influxdb import InfluxDBClient
import pandas as pd
import time

def getCollateral(measurement):
    res = client.query(f'SELECT {measurement} FROM {measurement} WHERE time>=now() -1m limit 1;')
    getcpu=list(res.get_points(measurement=measurement))
    df = pd.DataFrame(getcpu)
    return df[measurement][0]

if __name__ == '__main__':
    client = InfluxDBClient(host='localhost', port=8086, database='bots')
    measurements = [
                'bf_collateral',
                'bf_SpotCollateral',
                'bybit_collateral'
            ]
    while True:
        try:
            l = []
            for measurement in measurements:
                l.append(getCollateral(measurement))
            data = [{"measurement": "sum_collateral", "fields": {
              'sum_collateral': sum(l)}}]
            client.write_points(data)
        except:
            pass
        time.sleep(60)
