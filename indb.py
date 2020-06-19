from influxdb import InfluxDBClient

class indb:
    def __init__(self):
        self.client = InfluxDBClient(host='monpi.lan', port=8086)
    
    def push_db(self, json_body, series):
        try:
            self.client.switch_database(series)
            self.client.write_points(json_body)
        except:
            print("error: writing to database")

    def create_body(self, stuff):
        json_body = []
        for i in stuff: 
            json_body.append({"measurement": , "fields":})
