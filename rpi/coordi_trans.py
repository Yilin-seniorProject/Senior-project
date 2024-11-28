import cv2
import numpy as np
from ultralytics import YOLO


class Detect():

    def __init__(self, cameraMatrix, dist, outputPath, yoloPath):
        self.cameraMatrix = cameraMatrix
        self.camCenter_x = cameraMatrix[0][2]
        self.camCenter_y = cameraMatrix[1][2]
        self.focus_x = cameraMatrix[0][0]
        self.focus_y = cameraMatrix[1][1]
        self.outputPath = outputPath
        self.yoloPath = yoloPath
        self.row = np.deg2rad(row)
        self.pitch = np.deg2rad(pitch)
        self.heading = np.deg2rad(heading)
        self.dist = dist
        self.model = YOLO(yoloPath)
        self.i = 0 #just regarding as a file name to saving image, you can remove it

    def undistortion(self, img): #TODO fix undistortion
        h, w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(self.cameraMatrix, self.dist, (w,h), 0, (w,h)) #get new camera matrix
        dst = cv2.undistort(img, self.cameraMatrix, self.dist, None, newcameramtx)# undistort
        x, y, w, h = roi  # crop the image
        dst = dst[y:y+h, x:x+w]
        return dst #TODO check new camera mtx
    
    def detect(self, img):
        obj = []
        dst = self.undistortion(img)
        results = self.model.predict(dst)
        boxes = results[0].boxes #get boxes
        for box in boxes:
            id = int(box.cls) 
            xy_arr = box.xyxy.cpu()
            coordi = np.array(xy_arr)
            x_mid = (coordi[:, 0] + coordi[:, 2]) / 2
            y_mid = (coordi[:, 1] + coordi[:, 3]) / 2
            obj.append([id, x_mid, y_mid])
            annotaionImg = results[0].plot()
        if len(obj)>0:
            print(self.i)
            cv2.imwrite(f'{self.outputPath}/{self.i}.jpg', annotaionImg) #save image when detect obj
            self.i+=1
            return obj
        
    def coordinateTransform(self, img, row, pitch, heading, height, longitude, latitude):
        #caclulate origin of the camrea
        newOrigin = [] #(cx, cy)
        newOrigin.append(self.camCenter_x - np.tan(row))
        newOrigin.append(self.camCenter_y - np.tan(pitch))
        #calculate offset
        objs = self.detect(img)
        if len(objs)>0:
            rot = [] # result for rotate coordinate
            for obj in objs:
                x_offset = (obj[1]-newOrigin[0])*height / self.focus_x
                y_offset = (obj[2]-newOrigin[1])*height / self.focus_y
                x_north = x_offset*np.cos(heading) - y_offset*np.sin(heading) #rotation mtx = ([cos -sin],[sin cos])
                y_north = x_offset*np.sin(heading) + y_offset*np.cos(heading)
                longi = x_north/101779 #longitude offset
                lati = y_north/110936.2 #latitude offset
                precise_longi = longitude+longi
                precise_lati = latitude+lati

                # 2d list and it has id, north coordinate(x,y), corrected GPS(經,緯)
                # actually like this: [[3, array([-2.2423], dtype=float32), array([-1.2744], dtype=float32), array([100]), array([100], dtype=float32)]]
                rot.append([obj[0], x_north, y_north, precise_longi, precise_lati]) 
            return rot
        else:
            objs = self.detect()

if __name__ =='__main__':
    camera_mtx = np.array( [[1.84463584e+03, 0.00000000e+00, 1.37568753e+02],
                            [0.00000000e+00, 1.74529878e+03, 2.78409056e+02],
                            [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    dist = np.array([[ 9.66082944e-02,  5.06778169e+00, -4.60461075e-03, -6.56564683e-02, -2.41323529e+01]])
    model_path = r"best_ncnn_model"
    input = r'video1115_1244.mp4'
    output_path = r"" #path for saving captured images
    
    height = 20  #altitude
    
    #attitude
    row = 0 
    pitch = 0
    heading = 100  

    # detedctor = Detect(camera_mtx, dist, output_path, model_path)
    # cap = cv2.VideoCapture(input)
    # ret, frame = cap.read()
    # while ret:
    #     arg = detedctor.coordinateTransform(frame, row, pitch, heading, height, longitude, latitude)
    #     if len(arg)==1:
    #         ret, frame = cap.read()
    #         continue
    #     distance = (arg[1][1][0]-arg[0][1][0])**2+(arg[1][2][0]-(arg[0][2][0]))**2
    #     print(f'test_distance = {np.sqrt(distance)}')
    #     ret, frame = cap.read()