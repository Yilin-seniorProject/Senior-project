from flask import Flask, render_template, g, request, jsonify
import json, sqlite3, os, base64, io
from PIL import Image
from pyngrok import ngrok



app = Flask(__name__)
DATABASE = 'database.db'
table_name = 'point'
image_counter = 1
sended = "0.jpg"

def save_image(image):
    global image_counter
    save_directory = 'web\static'
    os.makedirs(save_directory, exist_ok=True)
    image_name = str(image_counter)+'.jpg'
    image_binary = base64.b64decode(image)
    image = Image.open(io.BytesIO(image_binary))
    image.save(os.path.join(save_directory, image_name), 'JPEG')
    image_counter += 1
    return(image_name)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    if db is not None:
        print('conective')
    return db

@app.teardown_appcontext
def close_db(exception=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#主介面
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

#次頁面
@app.route('/proposal_history.html')
def proposal_history():
    return render_template('proposal_history.html')
@app.route('/project_members.html')
def project_members():
    return render_template('project_members.html')

#傳遞初始數據給前端
'''
@app.route('/initial_data', methods=['GET'])
def initial_data():
    global sended
    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute("SELECT ImageName, Latitude, Longitude, ImageType FROM {}".format(table_name))
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    if data:
        sended = data[-1]['ImageName']
        return jsonify({"status": "success", "message": "Data retrieved", "data": data})
    else:
        # 返回提示數據列表為空
        return jsonify({"status": "error", "message": "No data found"})
'''

#後續數據更新傳遞前端
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

#接收前端要求(傳圖)
@app.route('/submit_data', methods=['GET'])
def submit_data():
    db = get_db()
    cursor = db.cursor()
    db.row_factory = sqlite3.Row

    image_name = request.args.get('image_name')#接收前端數據

    #取資料
    cursor.execute("SELECT ImageData FROM {} WHERE ImageName = ?".format(table_name), (image_name,))
    imagedata = cursor.fetchone()
    return jsonify({"status": "success", "message": "Data received"})

#接收樹梅派數據(傳來的有經緯、座標中點、圖、型別)
@app.route('/read_data', methods=['POST'])
def read_data():
    data = request.get_data('data')
    db = get_db()
    cursor = db.cursor()
    corddata = json.loads(data)
    latitude, longitude = corddata['geo']
    print('Received data:', data)
    try:
        name = save_image(corddata['img'])
        print(name)
        cursor.execute("INSERT INTO {} (ImageName, Center, Longitude, Latitude, ImageType) VALUES (?, ?, ?, ?, ?)".format(table_name), 
    (
        name,
        corddata['midpoints'],
        longitude,
        latitude,
        corddata['classname']
    ))
        db.commit()
        return jsonify({"status": "success", "message": "Data received"})
    except:
        return jsonify({"status": "fail", "message": "Data not received"})
    

@app.route('/delete_data', methods=['GET'])
def delete_data():
    global image_counter, sended
    image_counter = 1
    password = '1'
    key = request.args.get('key')
    if key != password:
        return jsonify({"status": "fail", "message": "wrong key"})
    db = get_db()
    cursor = db.cursor()
    table_name = 'point'
    cursor.execute("DELETE FROM {}".format(table_name))
    db.commit()
    sended = "0.jpg"
    return jsonify({"status": "success", "message": "Data deleted"})

if __name__ == '__main__':
    '''
    ngrok.set_auth_token("2lCGJJzd2hX7vPZs3eDtOaLiasl_5YdkT5A6wpaaujcqrffZQ")
    port = 5000
    public_url = ngrok.connect(port).public_url
    print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))
    '''
    app.run(host='127.0.0.1', port=5000, debug=True)