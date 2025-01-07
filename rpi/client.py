from json import dumps
from time import sleep
import mavlink
import predict
import requests


URL = 'http://192.168.137.1:5000/read_data'

while True:
    try:
        result = predict.predict()

        if result != None:
            frame, classname, midpoints = result
            lat, lon, alt = mavlink.get_gps_info()  # 未修正

            data = dumps({
                'frame': frame,
                'geo': (lat, lon),
                'classname': classname,
                })

            response = requests.post(URL, json=data)
    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        print(e)
    else:
        print(response.status_code)
        print(response.text)
    finally:
        sleep(0.1)