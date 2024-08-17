from json import dumps
import mavlink
import predict
import requests

# URL = 'https://55c6-140-115-205-49.ngrok-free.app/dataCollector'
URL = '127.0.0.1:5000/read_data'

while True:
    result = predict.predict()
    
    if result != None:
        frame, classname, accuracy, midpoints = result
        lat, lon = mavlink.get_gps_info()
        geo = dumps({
            "lat":lat,
            "lng":lon
            })

        data = {'img':open(frame, 'rb'),
                'classname': classname,
                'midpoints': midpoints,
                'geo':geo}
        
        request = requests.post(URL, files=data)
        print(request)

