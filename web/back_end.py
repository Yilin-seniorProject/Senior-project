from flask import Flask, render_template, g, request, jsonify
import json
import sqlite3
import os
import numpy as np
import cv2
from datetime import datetime


app = Flask(__name__)
DATABASE = 'database.db'
IMAGE_DIRECTORY = r'web\static\car_image'
CAMERA_MATRIX = np.array([[1.84463584e+03, 0, 1.37568753e+02],
                       [0, 1.74529878e+03, 2.78409056e+02],
                       [0, 0, 1]])

table_name = 'point'
cleantag = False

# Define coordinate transform fuction
def coordinateTransform(camera_mtx:np.ndarray, obj:tuple, position:tuple, attitude:tuple) -> tuple:
    """_Summary_
    Args:
        camera_mtx (np.ndarray): camera matrix
        obj (Tuple): x_mid, y_mid
        position (Tuple): latitude, longitude, alt, heading
        attitude (Tuple): roll, pitch

    Returns:
        out(Tuple): precise longitude, precise latitude
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
    newOrigin.append(camera_mtx[0, 2] - np.tan(roll))
    newOrigin.append(camera_mtx[1, 2] - np.tan(pitch))
    # calculate offset
    # result for rotate coordinate
    x_offset = (obj[0]-newOrigin[0]) * alt / camera_mtx[0, 0]
    y_offset = (obj[1]-newOrigin[1]) * alt / camera_mtx[1, 1]
    x_north = x_offset*np.cos(hdg) - y_offset*np.sin(hdg)  # rotation mtx = ([cos -sin],[sin cos])
    y_north = x_offset*np.sin(hdg) + y_offset*np.cos(hdg)
    longi = x_north / 100827.79149792079  # longitude offset(經度)
    lati = y_north / 111194.99645772896  # latitude offset
    precise_longi = lon + longi
    precise_lati = lat + lati

    # 2d list and it has id, north coordinate(x,y), corrected GPS(經,緯)
    return (precise_longi, precise_lati)

# 連接sql
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    if db is not None:
        print('conective')
    return db

# 自動關閉sql
@app.teardown_appcontext
def close_db(exception=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# 圖片檔儲存(list -> np.array，回傳target_img)
def save_image(image):
    global IMAGE_DIRECTORY
    sys_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    image = np.array(image)
    image_name = f'{sys_datetime}.jpg'
    image_path = os.path.join(IMAGE_DIRECTORY, image_name)
    cv2.imwrite(image_path, image)
    print(f"Saving image at: {image_path}")
    return image_name


# 清理圖片資料夾
def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # 删除文件
            elif os.path.isdir(file_path):
                os.rmdir(file_path)  # 删除空文件夹
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

# 頁面載入
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')



# 前端使用介面
# 更新數據
@app.route('/update_data', methods=['GET'])
def update_data():
    global cleantag
    if cleantag:
        cleantag = False
        return jsonify({"message": "The database is empty"})
    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    query = f"SELECT target_img, Latitude, Longitude, target_type, drone_lat, drone_lng, message FROM {table_name}"
    cursor.execute(query)
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    if data:
        return jsonify(data)
    else:
        # 返回提示數據列表為空
        return jsonify({"message": "No updated data found"})

# 提取圖片
@app.route('/submit_data', methods=['GET'])
def submit_data():
    marker_id = request.args.get('marker_id')

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        f"SELECT target_img FROM {table_name} WHERE ROWID = ?", (marker_id,))
    target_img = cursor.fetchone()
    cursor.execute(
        f"SELECT drone_lat, drone_lng, drone_alt FROM {table_name} WHERE ROWID = ?", (marker_id,))
    drone_info = cursor.fetchone()
    cursor.execute(
        f"SELECT message FROM {table_name} WHERE ROWID = ?", (marker_id,))
    message = cursor.fetchone()
    if target_img is not None and drone_info is not None and message is not None:
        target_img = target_img[0]
    else:
        return jsonify({"status": "error", "message": "No data found"})
    image_path = os.path.join("static", "car_image", target_img)
    return jsonify({"image_path": image_path, "drone_info": drone_info, "message":message})


@app.route("/read_data", methods=["POST"])
def read_data():
    if request.method == "POST":
        db = get_db()
        cursor = db.cursor()
        try:
            response = request.get_json()
            data = json.loads(response)
            name = save_image(data['frame'])
            drone_lat = data['drone_lat']
            drone_lng = data['drone_lng']
            drone_alt = data['drone_alt']
            drone_pitch = data['drone_pitch']
            drone_roll = data['drone_roll']
            drone_head = data['drone_head']
            ids = data['classname']
            message = data['message']
            mids = data['center']
            drone_pos = (drone_lat, drone_lng, drone_alt, drone_head)
            drone_att = (drone_roll, drone_pitch)
            for i in range(len(ids)):
                centerX, centerY = mids[i]
                message = message[i]
                target_objs = (centerX, centerY)
                if ids[i] == 0:
                    target_type = 'car'
                elif ids[i] == 1:
                    target_type = 'motorcycle'
                elif ids[i] == 2:
                    target_type = 'pedestrian'
            
                result = coordinateTransform(CAMERA_MATRIX, target_objs, drone_pos, drone_att)
                longitude, latitude = result
                data_add_query = f"INSERT INTO {table_name} (" + \
                                                "target_img," + \
                                                "Longitude," + \
                                                "Latitude," + \
                                                "target_type," + \
                                                "CenterX," + \
                                                "CenterY," + \
                                                "drone_lat," + \
                                                "drone_lng," + \
                                                "drone_alt," + \
                                                "drone_pitch," + \
                                                "drone_roll," + \
                                                "drone_head," + \
                                                "message" + \
                                                ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                cursor.execute(data_add_query,
                    (
                    name,
                    longitude,
                    latitude,
                    target_type,
                    centerX,
                    centerY,
                    drone_lat,
                    drone_lng,
                    drone_alt,
                    drone_pitch,
                    drone_roll,
                    drone_head,
                    message
                    ))
                db.commit()
            return jsonify({"status": "success", "message": "Data received"})
        except Exception as e:
            print(e)
            return jsonify({"status": "fail", "message": "Data not written"})

# 清除數據庫
# 無安全保護，之後可能要加
@app.route('/delete_data', methods=['GET'])
def delete_data():
    global sended, IMAGE_DIRECTORY, cleantag
    clear_folder(IMAGE_DIRECTORY)
    db = get_db()
    cursor = db.cursor()
    table_name = 'point'
    cursor.execute("DELETE FROM {}".format(table_name))
    db.commit()
    sended = 0
    cleantag = True
    return jsonify({"status": "success", "message": "Data deleted"})

# rpi: host='192.168.137.1'; pc:host='127.0.0.1'
if __name__ == '__main__':
    try:
        host = '192.168.137.1'
        app.run(host=host, port=5000, debug=True)
    except:
        host = '127.0.0.1'
        app.run(host=host, port=5000, debug=True)
