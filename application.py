import sqlite3
from flask import Flask, request, abort

app = Flask(__name__)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)