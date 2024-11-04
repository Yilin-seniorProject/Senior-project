from flask import Flask, render_template, g, request, jsonify
import json
import sqlite3
import os
import base64
import io
from PIL import Image
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


# 圖片檔儲存(格式二進位>jpg，輸入二進位圖片回傳ImageName)
def save_image(image):
    global IMAGE_DIRECTORY
    os.makedirs(IMAGE_DIRECTORY, exist_ok=True)
    sys_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_name = str(sys_datetime)+'.jpg'
    # image_binary = base64.b64decode(image)
    # image = Image.open(io.BytesIO(image_binary))
    image = Image.open(io.BytesIO(image))
    full_image_path = os.path.join(IMAGE_DIRECTORY, image_name)
    print(f"Saving image at: {full_image_path}")
    image.save(full_image_path, 'JPEG')
    return (image_name)


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


@app.route('/read_data', methods=['POST'])
def read_data():
    data = request.get_data('data')
    db = get_db()
    cursor = db.cursor()
    corddata = json.loads(data)
    try:
        name = save_image(corddata['img'])
        geo_data = json.loads(corddata['geo'])
        latitude = geo_data['lat']
        longitude = geo_data['lng']
        imagetype = corddata['classname']
        center = corddata['midpoints']
        cursor.execute("INSERT INTO {} (ImageName, Center, Longitude, Latitude, ImageType) VALUES (?, ?, ?, ?, ?)".format(table_name),
                       (
            name,
            center,
            longitude,
            latitude,
            imagetype
        ))
        db.commit()
        return jsonify({"status": "success", "message": "Data received"})
    except:
        return jsonify({"status": "fail", "message": "Data not received"})

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
    app.run(host='127.0.0.1', port=5000, debug=True)
