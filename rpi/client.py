from json import dumps
from time import sleep
import mavlink
import predict
import requests


URL = 'http://192.168.137.1:5000/read_data'

while True:
    result = predict.predict()

    if result != None:
        frame, classname, accuracy, midpoints = result
        lat, lon = mavlink.get_gps_info()
        geo = dumps({
            "lat": lat,
            "lng": lon
        })

        data = {'img': open(frame, 'rb'),
                'classname': classname,
                'midpoints': midpoints,
                'geo': geo
                }

        request = requests.post(URL, files=data)
        sleep(0.1)