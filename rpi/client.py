import cv2
import mavlink
import requests
import numpy as np
from time import sleep
from json import dumps
from coordi_trans import Detector, picam2


URL = 'http://192.168.137.1:5000/read_data'
camera_mtx = np.array([[1.84463584e+03, 0, 1.37568753e+02],
                       [0, 1.74529878e+03, 2.78409056e+02],
                       [0, 0, 1]])
dist = np.array([[9.66082944e-02,  5.06778169e+00,
                -4.60461075e-03, -6.56564683e-02, -2.41323529e+01]])
model_path = r"best_ncnn_model"


while True:
    try:
        detector = Detector(cameraMatrix=camera_mtx,
                            dist=dist, yoloPath=model_path)
        frame = picam2.capture_array()
        position = mavlink.get_gps_info()
        attitude = mavlink.get_attitude_info()
        result = detector.coordinateTransform(
            frame, position, attitude)
        if len(result) != 0:
            for rot in result:
                id, x_north, y_north, lon, lat, outputPath = rot
                img = cv2.imread(outputPath)
                data = dumps({
                    'frame': img.tolist(),
                    'geo': (lat.tolist(), lon.tolist()),
                    'classname': id,
                    'center': (x_north.tolist(), y_north.tolist()),
                    'drone_lat': position[0],
                    'drone_lng': position[1],
                    'drone_alt': position[2],
                    'drone_head': position[3],
                    'drone_roll': attitude[0],
                    'drone_pitch': attitude[1],
                })

            response = requests.post(URL, json=data)
            print(response.status_code)
            print(response.text)
    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        print(e)
        exit(1)
    finally:
        sleep(0.1)