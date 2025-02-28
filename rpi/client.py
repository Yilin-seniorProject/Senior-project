import cv2
import mavlink
import requests
import numpy as np
from time import sleep
from json import dumps
from coordi_trans import Detector, picam2


URL = 'http://192.168.137.1:5000/read_data'


def block(frame, position, attitude):
    car_bbox = []
    red_mask = detector.detect_red_lines(frame)
    results = detector.detect(frame)
    if len(results) != 0:
        #加frame
        ids, mids, violations = [], [], []
        for result in results:
            id, x_mid, y_mid, x_1, y_1, x_2, y_2 = result # x_mid, y_mid means bounding box center
            ids.append(id)
            mids.append([x_mid.tolist()[0], y_mid.tolist()[0]])
            if id == 0:
                car_bbox.append((int(x_1), int(y_1), int(x_2), int(y_2)))
            elif id ==1:
                car_bbox.append((int(x_1), int(y_1), int(x_2), int(y_2)))
            else:
                car_bbox.append((int(x_1), int(y_1), int(x_2), int(y_2)))
        for i, (x1, y1, x2, y2) in enumerate(car_bbox):
            is_violating = detector.check_parking_violation(x1, y1, x2, y2, red_mask)
            if is_violating:
                msg = f"Object {i+1} is violating parking rule by being on red line."
                cv2.rectangle(frame, (x_1, y_1), (x_2, y_2), (255, 0, 0), 2)
            else:
                msg = f"Object {i+1} is not violating parking rule."
            print(msg)
            violations.append(int(is_violating))

        data = dumps({
            'frame': frame.tolist(),
            'classname': ids,
            'center': mids,
            'message': violations,
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

def img_capture():
    frame = picam2.capture_array()
    position = mavlink.get_gps_info()
    attitude = mavlink.get_attitude_info()
    return [frame, position, attitude]


camera_mtx = np.array([[1.84463584e+03, 0, 1.37568753e+02],
                       [0, 1.74529878e+03, 2.78409056e+02],
                       [0, 0, 1]])
dist = np.array([[9.66082944e-02,  5.06778169e+00,
                -4.60461075e-03, -6.56564683e-02, -2.41323529e+01]])
model_path = r"best_ncnn_model"
detector = Detector(cameraMatrix=camera_mtx,
                    dist=dist, yoloPath=model_path)
frames = []
print('Detector is on ready')

frames.append(img_capture())
frames.append(img_capture())
print('image captured')

while True:
    try:
        bool = detector.drop_img(frames[0][0], frames[1][0])
        print(bool)
        if bool==True:
            print('find similar image')
            frames[0] = frames[1]
            frames.pop()
            for f in frames:
                block(f[0], f[1], f[2])
            frames.append(img_capture())
        else:
            for f in frames:
                block(f[0], f[1], f[2])
            frames[0] = frames[1]
            frames.pop()
            print(len(frames[0]))
            frames.append(img_capture())

    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        print(e)
        exit(1)
    finally:
        sleep(0.1)



