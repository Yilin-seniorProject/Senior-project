from flask import Flask, render_template
import sqlite3


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)