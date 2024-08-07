from flask import Flask, render_template, g, request, jsonify
import sqlite3


app = Flask(__name__)
DATABASE = 'database.db'

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
@app.route('/')
def index():
    return render_template('index.html')

#次頁面
@app.route('/proposal_history.html')
def proposal_history():
    return render_template('proposal_history.html')
@app.route('/project_members.html')
def project_members():
    return render_template('project_members.html')

#接收前端要求
@app.route('/submit_data', methods=['GET'])
def submit_data():
    db = get_db()
    cursor = db.cursor()
    db.row_factory = sqlite3.Row
    table_name = 'point'
    image_name = request.args.get('image_name')#接收前端數據

    #取資料
    cursor.execute("SELECT ImageData FROM {} WHERE ImageName = ?".format(table_name), (image_name,))
    imagedata = cursor.fetchone()
    cursor.execute("SELECT Longitude FROM {} WHERE ImageName = ?".format(table_name), (image_name,))
    longitude = cursor.fetchone()
    cursor.execute("SELECT Latitude FROM {} WHERE ImageName = ?".format(table_name), (image_name,))
    latitude = cursor.fetchone()
    return render_template('index.html', imagedata=imagedata, longitude=longitude, latitude=latitude)

#接收樹梅派數據
@app.route('/read_data', methods=['POST'])
def read_data():
    data = request.json.get('data')





if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)