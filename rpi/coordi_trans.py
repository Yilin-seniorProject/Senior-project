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
        tmp = []
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
            annotaionImg = results[0].plot()
            self.now = datetime.datetime.now()
            self.now = datetime.datetime.strftime(self.now, "%m%d_%H%M%S")
            self.outputPath = f'rpi/static/imgs/img{self.now}.jpg'
            tmp.append([id, x_mid, y_mid, self.outputPath])
        if len(tmp) > 0:
            cv2.imwrite(f'{self.outputPath}', annotaionImg)  # save image when detect obj    
        return tmp

    def drop_img(self, img_1, img_2):
        orb = cv2.ORB_create()
        
        kp_1, des_1 = orb.detectAndCompute(img_1, None)
        kp_2, des_2 = orb.detectAndCompute(img_2, None)

        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True)
        matches = bf.match(des_1, des_2)
        matches = sorted(matches, key = lambda x: x.distance)
        sim_Thres = 0.1*len(kp_1)
        if len(matches) > sim_Thres:
            return True
        else:
            return False


if __name__ =='__main__':
    camera_mtx = np.array( [[1.84463584e+03,              0, 1.37568753e+02],
                            [             0, 1.74529878e+03, 2.78409056e+02],
                            [             0,              0,              1]])
    dist = np.array([[ 9.66082944e-02,  5.06778169e+00, -4.60461075e-03, -6.56564683e-02, -2.41323529e+01]])
    model_path = r"best_ncnn_model"
    
    # # attitude
    detector = Detector(cameraMatrix = camera_mtx, dist = dist, yoloPath = model_path)
    img_1 = cv2.imread(r'rpi/static/imgs/img0122_180714.jpg')
    img_2 = cv2.imread(r'rpi/static/imgs/img0117_153242.jpg')
    print(detector.drop_img(img_1, img_2))