from picamera2 import Picamera2
from ultralytics import YOLO
import numpy as np

model = YOLO("./modelv3.pt")

picam2 = Picamera2()
picam2.preview_configuration.main.size = (1288, 720)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.main.align()
picam2.configure("preview")
picam2.start()

print("predict on ready")


def predict() -> tuple | None:
    frame = picam2.capture_array()
    result = model.predict(frame, conf=0.5)
    boxes = result[0].boxes
    for box in boxes:
        id = int(box.cls)
        classname = model.names[id]
        accuracy = box.conf.item()
        # print(box.cls.item())
        # print(box.xyxy)
        print(f"class: {classname}")
        print(f"accuracy: {accuracy}")
        xy_arr = box.xyxy.cpu()
        coordi = np.array(xy_arr)
        x_mid = (coordi[:, 0]+coordi[:, 2]) / 2
        y_mid = (coordi[:, 1]+coordi[:, 3]) / 2
        midpoints = np.column_stack((x_mid, y_mid))
        print(f"mid point(x,y): {midpoints}")

    return (frame, classname, accuracy, midpoints)
