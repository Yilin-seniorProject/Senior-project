from flask import Flask, render_template, g, request, jsonify
import json
import sqlite3
import os
import numpy as np
import cv2
from datetime import datetime

app = Flask(__name__)
DATABASE = 'database.db'
table_name = 'point'
cleantag = False
IMAGE_DIRECTORY = 'web\static\car_image'


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


# 圖片檔儲存(list -> np.array，回傳ImageName)
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

@app.route('/proposal_history.html')
def proposal_history():
    return render_template('proposal_history.html')

@app.route('/project_members.html')
def project_members():
    return render_template('project_members.html')


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
    query = "SELECT ImageName, Latitude, Longitude, ImageType FROM {}".format(
        table_name)
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
        f"SELECT ImageName FROM {table_name} WHERE ROWID = ?", (marker_id,))
    imagename = cursor.fetchone()
    if imagename is not None:
        imagename = imagename[0]
    else:
        return jsonify({"status": "error", "message": "No data found"})
    image_path = os.path.join("static", "car_image", imagename)
    return jsonify({"image_path": image_path})


@app.route("/read_data", methods=["POST"])
def read_data():
    if request.method == "POST":
        db = get_db()
        cursor = db.cursor()
        try:
            response = request.get_json()
            data = json.loads(response)
            name = save_image(data['frame'])
            latitude, longitude = data['geo']
            imagetype = data['classname']
            centerX, centerY = data['center']
            cursor.execute("INSERT INTO {} (ImageName, Longitude, Latitude, ImageType, CenterX, CenterY) VALUES (?, ?, ?, ?, ?, ?)".format(table_name),
                           (
            name,
            longitude,
            latitude,
            imagetype,
            centerX,
            centerY
            ))
            db.commit()
            return jsonify({"status": "success", "message": "Data received"})
        except Exception as e:
            print(e)
            return jsonify({"status": "fail", "message": "Data not received"})

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


if __name__ == '__main__':
    app.run(host='192.168.137.1', port=5000, debug=True)
