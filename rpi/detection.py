
from pathlib import Path
from collections import OrderedDict, namedtuple
import cv2
import random
import numpy as np
import onnxruntime as ort

class ObjectDetector:
    def __init__(self, model_path, names, cuda=True):
        self.model_path = model_path
        self.names = names
        self.providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if cuda else ['CPUExecutionProvider']
        self.session = ort.InferenceSession(self.model_path)
        self.colors = {name: [random.randint(0, 255) for _ in range(3)] for name in self.names}

    def letterbox(self, im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleup=True, stride=32):
        # Resize and pad image while meeting stride-multiple constraints
        shape = im.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not scaleup:
            r = min(r, 1.0)

        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]

        if auto:
            dw, dh = np.mod(dw, stride), np.mod(dh, stride)

        dw /= 2
        dh /= 2

        if shape[::-1] != new_unpad:
            im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)

        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
        return im, r, (dw, dh)

    def Pixel2Meter(self, point, height, focalLength):
        x = point[0]*(height-focalLength)/focalLength
        y = point[1]*(height-focalLength)/focalLength
        return [x,y]

    def detect(self, img_path, save_path):
        img = cv2.imread(img_path)
        img2 = img.copy()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image = img.copy()
        image, ratio, dwdh = self.letterbox(image, auto=False)
        image = image.transpose((2, 0, 1))
        image = np.expand_dims(image, 0)
        image = np.ascontiguousarray(image).astype(np.float32) / 255.0

        inname = [i.name for i in self.session.get_inputs()]
        inp = {inname[0]: image}
        outputs = self.session.run(None, inp)[0]
        ori_images = [img.copy()]

        for i, (batch_id, x0, y0, x1, y1, cls_id, score) in enumerate(outputs):
            print(x0, y0, x1, y1)
            image = ori_images[int(batch_id)]
            box = np.array([x0, y0, x1, y1])
            box -= np.array(dwdh * 2)
            box /= ratio
            box = box.round().astype(np.int32).tolist()
            cls_id = int(cls_id)
            score = round(float(score), 3)
            name = self.names[cls_id]
            color = self.colors[name]
            name += ' ' + str(score)
            cameraDocs = np.array([[1220, 0, 419], [0, 1160, 213],[0, 0, 1]])
            o_point = [x0-320, y0-240]
            e_point = [x1-320, y1-240]
            print(o_point, e_point)
            o_point = self.Pixel2Meter(o_point, height=20, focalLength=28e-3)
            e_point = self.Pixel2Meter(e_point, height=20, focalLength=28e-3)
            print(o_point, e_point)
            F_w = 640
            F_h = 480
            theta_h = np.arctan(cameraDocs[1][2]/cameraDocs[1][1])
            theta_w = np.arctan(cameraDocs[0][2]/cameraDocs[0][0])
            alpha = ((e_point[1]-0.2*F_h)*(theta_h/F_h))
            L_y = 20/np.tan(alpha)
            beta = ((o_point[0]+e_point[0]-F_w)*theta_w/2*F_w)
            L_x = L_y*np.tan(beta)
            print(f'class index is: {cls_id}')
            print(f'class name and confidence is: {name}')
            # print(f'conf is: {score}')
            print(f'bounding bos is: {x0}, {y0}, {x1}, {y1}')
            print(f'mid point is: {(x0+x1)/2}, {(y0+y1)/2}')
            print(f"物體距離無人機為x方向偏移 {L_x}m, y方向偏移 {L_y}m")
            print(f'物體偏移無人機的經緯度為{L_x/101779}, {L_y/110936.2}')

            cv2.rectangle(img2, box[:2], box[2:], color, 2)
            cv2.putText(img2, name, (box[0], box[1] - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.75, [225, 255, 255], thickness=2)
        cv2.imwrite(f'{save_path}.jpg', img2)
        # cv2.imshow('Detection Result', img2)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()


if __name__ == "__main__":
    model_path = r"runs\train\exp5\weights\best.onnx"
    classes = ['Bus', 'Car', 'Motorcycle', 'Truck']
    detector = ObjectDetector(model_path, classes)
    detector.detect(r'inference\0816_record\img0816_165630.jpg', r'runs\detect\test\test4')
