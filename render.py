from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('PATH TO HOME PAGE')

if __name__ == '__main__':
    app.run(debug=True)

    