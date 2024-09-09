from flask import Flask, render_template, g, request, jsonify
import json, sqlite3, os, base64, io
from PIL import Image

app = Flask(__name__)

DATABASE = 'database.db'
table_name = 'point'
image_counter, sended = int, str
IMAGE_DIRECTORY = 'web\static\car_image'

#連接sql
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    if db is not None:
        print('conective')
    return db

#自動關閉sql
@app.teardown_appcontext
def close_db(exception=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#初始化sql儲存
with app.app_context():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    cursor.execute("SELECT MAX(ROWID) FROM {}".format(table_name))
    latest_rowid = cursor.fetchone()[0]
    if latest_rowid:
        image_counter = latest_rowid + 1
        sended = str(latest_rowid) + '.jpg'
    else:
        image_counter = 1
        sended = "0.jpg"

#圖片檔儲存(格式base64>jpg，輸入base64編碼圖片回傳ImageName)
def save_image(image):
    global image_counter,IMAGE_DIRECTORY
    os.makedirs(IMAGE_DIRECTORY, exist_ok=True)
    image_name = str(image_counter)+'.jpg'
    image_binary = base64.b64decode(image)
    image = Image.open(io.BytesIO(image_binary))
    full_image_path = os.path.join(IMAGE_DIRECTORY, image_name)
    #print(f"Saving image at: {full_image_path}")
    image.save(full_image_path, 'JPEG')
    image_counter += 1
    return(image_name)

#圖片檔輸出(格式jpg>base64，輸入ImageName回傳圖片的base64編碼)
def trans_image(name):
    global IMAGE_DIRECTORY
    image_path = os.path.join(IMAGE_DIRECTORY, name)
    if not os.path.exists(image_path):
        return(None)
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return(encoded_string)

#清理圖片資料夾
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

#頁面載入
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
@app.route('/proposal_history.html')
def proposal_history():
    return render_template('proposal_history.html')
@app.route('/project_members.html')
def project_members():
    return render_template('project_members.html')


#前端使用介面
##更新數據
@app.route('/update_data', methods=['GET'])
def update_data():
    global sended
    #print(f"sended: {sended}, type: {type(sended)}")
    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    query = "SELECT ImageName, Latitude, Longitude, ImageType FROM {} WHERE ImageName > ?".format(table_name)
    cursor.execute(query, (sended,))
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    if data:
        sended = data[-1]['ImageName']
        return jsonify({"status": "success", "message": "Data retrieved", "data": data})
    else:
        # 返回提示數據列表為空
        return jsonify({"status": "error", "message": "No data found"})

##提取圖片
@app.route('/submit_data', methods=['GET'])
def submit_data():
    rowid = request.args.get('rowid')
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT ImageName FROM {} WHERE ROWID = ?".format(table_name), (rowid,))
    imagename = cursor.fetchone()
    if imagename is not None:
        imagename = imagename[0]
    else:
        return jsonify({"status": "error", "message": "No data found"})
    image = trans_image(imagename)
    if image:
        return jsonify({"status": "success", "image_data": image})
    else:
        return jsonify({"status": "error", "message": "No data found"})


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
    

@app.route('/delete_data', methods=['GET'])
def delete_data():
    global image_counter, sended, IMAGE_DIRECTORY
    '''
    password = '1'
    key = request.args.get('key')
    if key != password:
        return jsonify({"status": "fail", "message": "wrong key"})
    '''
    clear_folder(IMAGE_DIRECTORY)
    db = get_db()
    cursor = db.cursor()
    table_name = 'point'
    cursor.execute("DELETE FROM {}".format(table_name))
    db.commit()
    image_counter = 1
    sended = "0.jpg"
    return jsonify({"status": "success", "message": "Data deleted"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)