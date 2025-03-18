import cv2
import mavlink
import requests
import numpy as np
from time import sleep
from json import dumps
from detector import Detector, picam2


URL = 'http://192.168.137.1:5000/read_data'


def detect_violations(frame, position, attitude) -> None:
    car_bbox = []
    results = detector.detect(frame)
    if len(results) != 0:
        ids, mids, violations = [], [], []
        for result in results:
            id, x_mid, y_mid = result[:3] # x_mid, y_mid means bounding box center
            ids.append(id)
            mids.append([x_mid.tolist()[0], y_mid.tolist()[0]])
            bbox_int = list(map(lambda x: int(x[0]), result[3:]))
            car_bbox.append(bbox_int)
            
        _, red_mask = detector.detect_red_lines(frame, car_bbox)
        _, yellow_mask = detector.detect_yellow_net(frame, car_bbox) # 黃網線檢測(待實作)
        
        for i, (x1, y1, x2, y2) in enumerate(car_bbox):
            is_violating = detector.check_parking_violation(x1, y1, x2, y2, red_mask)
            yellow_net = detector.check_yellow_net_violation(x1, y1, x2, y2, yellow_mask)
            if is_violating or yellow_net:
                msg = f"Object {i+1} is violating parking rule by being on red line."
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            else:
                msg = f"Object {i+1} is not violating parking rule."
            print(msg)
            violations.append(int(is_violating))

        violation_data = dumps({
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

        response = requests.post(URL, json=violation_data)
        print(response.status_code)
        print(response.text)
        return None

def img_capture() -> list:
    frame = picam2.capture_array()
    position = mavlink.get_gps_info()
    attitude = mavlink.get_attitude_info()
    return [frame, position, attitude]

if __name__ == "__main__":
    camera_mtx = np.array([[1.84463584e+03, 0, 1.37568753e+02],
                        [0, 1.74529878e+03, 2.78409056e+02],
                        [0, 0, 1]])
    dist = np.array([[9.66082944e-02,  5.06778169e+00,
                    -4.60461075e-03, -6.56564683e-02, -2.41323529e+01]])
    model_path = r"best_ncnn_model"
    detector = Detector(cameraMatrix=camera_mtx,
                        dist=dist, yoloPath=model_path)
    print('Detector is on ready')

    frames = []
    frames.append(img_capture())
    frames.append(img_capture())
    print('image captured')

    while True:
        try:
            is_similar_img = detector.drop_img(frames[0][0], frames[1][0])
            if not is_similar_img:
                frames[0] = frames[1]
                for f in frames:
                    detect_violations(f[0], f[1], f[2])
            frames.pop()
            frames.append(img_capture())

        except KeyboardInterrupt:
            exit(0)
        except Exception as e:
            print(e)
        finally:
            sleep(0.1)