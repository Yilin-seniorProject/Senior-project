import cv2
import numpy as np
from picamera2 import Picamera2
from ultralytics import YOLO
import datetime


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
            tmp.append([id, x_mid, y_mid, coordi[:, 0], coordi[:, 1], coordi[:, 2], coordi[:, 3]])
        if len(tmp) > 0:
            cv2.imwrite(f'{self.outputPath}', annotaionImg)  # save image when detect obj    
        return tmp

    def drop_img(self, img_1, img_2):
        orb = cv2.ORB_create()
        kp_1, des_1 = orb.detectAndCompute(img_1, None)
        kp_2, des_2 = orb.detectAndCompute(img_2, None)

        if des_1 is None or des_2 is None:
           return False

        sim_Thres = 0.1*len(kp_1)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = False)
        matches = bf.knnMatch(des_1, des_2, k=2)
        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:  # Lowe's ratio test
                good_matches.append(m)
        if len(good_matches) > sim_Thres:
            return True
        else:
            return False

    # Function to detect red lines (red color mask)
    def detect_red_lines(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # Convert to HSV color space
        lower_red1 = np.array([0, 70, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 70, 50])
        upper_red2 = np.array([180, 255, 255])

        # Create masks to detect red color in two ranges
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = mask1 | mask2
        return red_mask

    # Function to check if a car is violating parking rules
    def check_parking_violation(self, x1, y1, x2, y2, red_mask):
        # Define areas around the car to check for red lines
        above_area = red_mask[max(0, y1 - 50):y1, x1:x2]
        below_area = red_mask[y2:y2 + 50, x1:x2]

        # Check if red lines exist in these regions
        above_red = np.any(above_area > 0)
        below_red = np.any(below_area > 0)

        return (above_red and below_red)



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