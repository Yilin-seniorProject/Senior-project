from flask import Flask, render_template
import sqlite3
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'web', 'template')
static_dir = os.path.join(current_dir, 'web', 'static')

app = Flask(__name__,template_folder=template_dir, static_folder=static_dir)

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

    