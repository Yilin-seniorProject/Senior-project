from flask import Flask, render_template, g
import sqlite3


app = Flask(__name__)
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_db():
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()



@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    return render_template('index.html')

@app.route('/proposal_history.html')
def proposal_history():
    return render_template('proposal_history.html')
@app.route('/project_members')
def project_members():
    return render_template('project_members.html')

if __name__ == '__main__':
    app.run(debug=True)

    