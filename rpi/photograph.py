import os
import datetime

now = datetime.datetime.now()
now = datetime.datetime.strftime(now, "%m%d_%H%M")

mode = input("拍照還是錄影[jpeg/vid]？ [jpeg/vid] ")
PATH = "./rpi/static/"
if mode == "jpeg":
    for i in range(10):
        fileName = PATH + f"imgs/img{now}{i}.jpg"
        os.system(
            f'libcamera-jpeg -o {fileName} -t 100 --width 640 --height 640')
elif mode == "vid":
    t = int(input("請輸入錄製時間(s): ")) * 1000
    fileName = PATH + f"videos/video{now}.h264"
    os.system(
        f'libcamera-vid -o {fileName} -t {t} --width 640 --height 480')

exit()
