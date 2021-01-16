from influxdb import InfluxDBClient
if __name__ == '__main__':
  client = InfluxDBClient(host='localhost', port=8086, database='bots')
  
  while True:
    pass
