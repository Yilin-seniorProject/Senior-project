import os
import datetime

now = datetime.datetime.now()
now = datetime.datetime.strftime(now, "%m%d_%H%M")

mode = input("拍照還是錄影[jpeg/vid]？ [jpeg/vid] ")

if mode == "jpeg":
    os.system(
        f'libcamera-jpeg -o ~/Drone/static/imgs/img{now}.jpg -t 100 --width 1920 --height 1080')
elif mode == "vid":
    t = int(input("請輸入錄製時間(s): ")) * 1000
    os.system(
        f'libcamera-vid -o ~/Drone/static/videos/video{now}.h264 -t {t} --width 640 --height 480')

exit()
