from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('PATH TO HOME PAGE')

@app.route('/about')
def about():
    return render_template('PATH TO ABOUT')

if __name__ == '__main__':
    app.run(debug=True)

    