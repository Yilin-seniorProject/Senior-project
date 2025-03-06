import cv2
import numpy as np
from picamera2 import Picamera2
from ultralytics import YOLO
from datetime import datetime


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
        self.dist = dist
        self.model = YOLO(yoloPath, task='detect')

    def undistortion(self, img):
        h, w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(self.cameraMatrix, self.dist, (w,h), 0, (w,h))  # get new camera matrix
        dst = cv2.undistort(img, self.cameraMatrix, self.dist, None, newcameramtx)  # undistort
        x, y, w, h = roi  # crop the image
        dst = dst[y:y+h, x:x+w]
        return dst
    
    def detect(self, img):
        detection_info = []
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
            now = datetime.now().strftime("%m%d_%H%M%S")
            outputPath = f'rpi/static/imgs/img{now}.jpg'
            detection_info.append([id, x_mid, y_mid, coordi[:, 0], coordi[:, 1], coordi[:, 2], coordi[:, 3]])
        if len(detection_info) > 0:
            cv2.imwrite(f'{outputPath}', annotaionImg)  # save image when detect object
        return detection_info

    def drop_img(self, img_1, img_2):
        orb = cv2.ORB_create()
        kp_1, des_1 = orb.detectAndCompute(img_1, None)
        _, des_2 = orb.detectAndCompute(img_2, None)

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
    def detect_red_lines(self, img:cv2.typing.MatLike, bbox_list:list=None) -> cv2.typing.MatLike:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_red1 = np.array([0, 70, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 70, 50])
        upper_red2 = np.array([180, 255, 255])

        # Create masks to detect red color in two ranges
        mask1 = cv2.inRange(img, lower_red1, upper_red1)
        mask2 = cv2.inRange(img, lower_red2, upper_red2)
        mask = mask1 | mask2
        if bbox_list is not None:
            for bbox in bbox_list:
                x0, y0, x1, y1 = bbox
                mask[y0:y1, x0:x1] = 0
        # mask = cv2.erode(mask, (3,3), iterations=5)
        # mask = cv2.dilate(mask, (5,5), iterations=10)
        lines = cv2.HoughLinesP(mask, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        if lines is not None:
            for line in lines:
                x0, y0, x1, y1 = line[0, :]
                cv2.line(img, (x0, y0), (x1, y1), (0, 255, 0), 2)
        return img, mask

    # Function to check if a car is violating parking rules
    def check_parking_violation(self, x1, y1, x2, y2, red_mask):
        # Define areas around the car to check for red lines
        above_area = red_mask[max(0, y1 - 10):y1, x1:x2]
        below_area = red_mask[y2:y2 + 10, x1:x2]

        # Check if red lines exist in these regions
        above_red = np.any(above_area > 0)
        below_red = np.any(below_area > 0)

        return (above_red and below_red)

    # Function to detect yellow net (yellow color mask)
    def detect_yellow_net(self, img:cv2.typing.MatLike, bbox_list:list=None) -> cv2.typing.MatLike:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([30, 255, 255])
        mask = cv2.inRange(img, lower_yellow, upper_yellow)
        if bbox_list is not None:
            for bbox in bbox_list:
                x0, y0, x1, y1 = bbox
                mask[y0:y1, x0:x1] = 0
        mask = cv2.erode(mask, (3,3), iterations=2)
        mask = cv2.dilate(mask, (5,5), iterations=10)
        return img, mask

    # Function to check if a car is occupy yellow net area
    def check_yellow_net_violation(self, x1, y1, x2, y2, yellow_mask) -> bool:
        above_area = yellow_mask[max(0, y1-10):y1, x1:x2]
        below_area = yellow_mask[y2:y2+10, x1:x2]
        left_area = yellow_mask[y1:y2, max(0, x1-10):x1]
        right_area = yellow_mask[y1:y2, x2:x2+10]

        above_yellow = np.any(above_area > 0)
        below_yellow = np.any(below_area > 0)
        left_yellow = np.any(left_area > 0)
        right_yellow = np.any(right_area > 0)

        #check if yellow lines exist at least three regions
        yellow_count = sum([above_yellow, below_yellow, left_yellow, right_yellow])

        return yellow_count >= 3


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