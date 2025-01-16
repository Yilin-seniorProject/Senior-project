import cv2
import numpy as np
from picamera2 import Picamera2
from ultralytics import YOLO
import datetime
from mavlink import get_attitude_info, get_gps_info

picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 640)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.main.align()
picam2.configure("preview")
picam2.start()

class Detector():
    def __init__(self, cameraMatrix, yoloPath, dist, **kwargs):
        # cameraMatrix, dist, outputPath, yoloPath
        self.cameraMatrix = cameraMatrix
        self.camCenter_x = self.cameraMatrix[0][2]
        self.camCenter_y = self.cameraMatrix[1][2]
        self.focus_x = self.cameraMatrix[0][0]
        self.focus_y = self.cameraMatrix[1][1]
        self.now = datetime.datetime.now()
        self.now = datetime.datetime.strftime(self.now, "%m%d_%H%M%S")
        self.outputPath = kwargs.get('outputPath', f'rpi/static/imgs/img{self.now}.jpg')
        self.dist = dist
        self.model = YOLO(yoloPath)

    def undistortion(self, img): # TODO:fix undistortion
        h, w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(self.cameraMatrix, self.dist, (w,h), 0, (w,h))  # get new camera matrix
        dst = cv2.undistort(img, self.cameraMatrix, self.dist, None, newcameramtx)  # undistort
        x, y, w, h = roi  # crop the image
        dst = dst[y:y+h, x:x+w]
        return dst  # TODO:check new camera mtx
    
    def detect(self, img):
        obj = []
        dst = self.undistortion(img)
        results = self.model.predict(dst)
        boxes = results[0].boxes  # get boxes
        for box in boxes:
            id = int(box.cls) 
            xy_arr = box.xyxy.cpu()
            coordi = np.array(xy_arr)
            x_mid = (coordi[:, 0] + coordi[:, 2]) / 2
            y_mid = (coordi[:, 1] + coordi[:, 3]) / 2
            obj.append([id, x_mid, y_mid])
            annotaionImg = results[0].plot()
        if len(obj) > 0:
            self.now = datetime.datetime.now()
            self.now = datetime.datetime.strftime(self.now, "%m%d_%H%M%S")
            self.outputPath = f'rpi/static/imgs/img{self.now}.jpg'
            cv2.imwrite(f'{self.outputPath}', annotaionImg)  # save image when detect obj
        return obj
        
    def coordinateTransform(self, img, position:tuple, attitude:tuple):
        """_Summary_
        Args:
            img (Matlike): Input image
            position (Tuple): lat, lon, alt
            attitude (Tuple): roll, pitch, hdg

        Returns:
            _type_: _description_
        """
        # img, roll, pitch, heading, height, longitude, latitude
        # caclulate origin of the camera
        newOrigin = []  # (cx, cy)
        roll = np.deg2rad(attitude[0])
        pitch = np.deg2rad(attitude[1])
        lat = position[0]
        lon = position[1]
        alt = position[2]
        hdg = np.deg2rad(position[3])
        rot = []
        newOrigin.append(self.camCenter_x - np.tan(roll))
        newOrigin.append(self.camCenter_y - np.tan(pitch))
        # calculate offset
        objs = self.detect(img)
        if len(objs) > 0:
         # result for rotate coordinate
            for obj in objs:
                x_offset = (obj[1]-newOrigin[0]) * alt / self.focus_x
                y_offset = (obj[2]-newOrigin[1]) * alt / self.focus_y
                x_north = x_offset*np.cos(hdg) - y_offset*np.sin(hdg)  # rotation mtx = ([cos -sin],[sin cos])
                y_north = x_offset*np.sin(hdg) + y_offset*np.cos(hdg)
                longi = x_north / 100827.79149792079  # longitude offset(經度)
                lati = y_north / 111194.99645772896  # latitude offset
                precise_longi = lon + longi
                precise_lati = lat + lati

                # 2d list and it has id, north coordinate(x,y), corrected GPS(經,緯)
                # actually like this: [[3, array([-2.2423], dtype=float32), array([-1.2744], dtype=float32), array([100]), array([100], dtype=float32)]]
                rot.append([obj[0], x_north, y_north, precise_longi, precise_lati, self.outputPath]) 
        return rot


if __name__ =='__main__':
    camera_mtx = np.array( [[1.84463584e+03,              0, 1.37568753e+02],
                            [             0, 1.74529878e+03, 2.78409056e+02],
                            [             0,              0,              1]])
    dist = np.array([[ 9.66082944e-02,  5.06778169e+00, -4.60461075e-03, -6.56564683e-02, -2.41323529e+01]])
    model_path = r"best_ncnn_model"
    
    # attitude
    detector = Detector(cameraMatrix = camera_mtx, dist = dist, yoloPath = model_path)
    while True:
        frame = picam2.capture_array()
        attitude = get_attitude_info()
        position = get_gps_info()
        print(detector.coordinateTransform(
            frame, position, attitude))