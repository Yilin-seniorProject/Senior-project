import cv2
import numpy as np
from coordi_trans import Detector

def image_processing(img:cv2.typing.MatLike, bbox_list:list=None) -> cv2.typing.MatLike:
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv_upper = np.array([180, 180, 180])
    hsv_lower = np.array([150, 60, 100])

    mask = cv2.inRange(img, hsv_lower, hsv_upper)
    if bbox_list is not None:
        for bbox in bbox_list:
            x0, y0, x1, y1 = bbox
            mask[y0:y1, x0:x1] = 0
    mask = cv2.erode(mask, (3,3), iterations=5)
    mask = cv2.dilate(mask, (5,5), iterations=10)
    lines = cv2.HoughLinesP(mask, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
    img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
    if lines is not None:
        for line in lines:
            x0, y0, x1, y1 = line[0, :]
            cv2.line(img, (x0, y0), (x1, y1), (0, 255, 0), 2)
    return img

if __name__ == "__main__":
    camera_mtx = np.array( [[1.84463584e+03,              0, 1.37568753e+02],
                            [             0, 1.74529878e+03, 2.78409056e+02],
                            [             0,              0,              1]])
    dist = np.array([[ 9.66082944e-02,  5.06778169e+00, -4.60461075e-03, -6.56564683e-02, -2.41323529e+01]])
    model_path = r"best_ncnn_model"
    detector = Detector(cameraMatrix=camera_mtx, dist=dist, yoloPath=model_path)
    
    test_img1 = cv2.imread(r'temp/test.jpg')
    result = detector.detect(test_img1)
    bbox_list = []
    for bbox in result:
        bbox = list(map(lambda x: int(x[0]), bbox[3:]))
        bbox_list.append(bbox)
    test_img1 = image_processing(test_img1)
    cv2.imshow('result1', test_img1)
    
    test_img2 = cv2.imread(r'temp/test2.jpg')
    result = detector.detect(test_img2)
    bbox_list = []
    for bbox in result:
        bbox = list(map(lambda x: int(x[0]), bbox[3:]))
        bbox_list.append(bbox)
    test_img2 = image_processing(test_img2, bbox_list)
    cv2.imshow('result2', test_img2)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    
    cap = cv2.VideoCapture(r'temp/video0220_1131.mp4')
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (width, height))
    while True:
        ret, frame = cap.read()
        if ret is None:
            break
        frame = image_processing(frame)
        cv2.imshow('frame', frame)
        
        out.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    out.release()
    cv2.destroyAllWindows()
