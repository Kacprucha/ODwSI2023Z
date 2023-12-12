from flask import Flask, render_template, request
from waitress import serve

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/reset')
def forget_password():
    return render_template('reset_password.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/home')
def dashboard():
    return render_template('home.html', username="Test")

if __name__ == "__main__":
    #serve(app, host="0.0.0.0", port=8000)
    app.run(host="0.0.0.0", port=8000)