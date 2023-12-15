from flask import Flask, render_template, request, flash
from waitress import serve
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

def is_str_complex(password):
    # Check if the password has at least 8 characters
    if len(password) < 8:
        return False

    # Check if the password has at least one number
    if not any(char.isdigit() for char in password):
        return False

    # Check if the password has at least one special character
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False

    # Check if the password has at least one capital letter
    if not any(char.isupper() for char in password):
        return False

    # If all conditions are met, return True
    return True

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/reset')
def forget_password():
    return render_template('reset_password.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password1 = request.form.get('password')
        password2 = request.form.get('confirm_password')
        category='error'

        #user = User.query.filter_by(email=email).first()
        #if user:
        #    flash('Email already exists.', category='error')
        if len(username) < 4:
            flash('Username must be greater than 3 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif not is_str_complex(password1):
            flash('Password must be at least 8 characters long, has at least one number, has at least one special character and has at least one capital letter.', category='error')
        else:
            flash('Evrything cool', category='sucesses')
            category = 'sucesses'
            
    return render_template('register.html', category=category)

@app.route('/home')
def dashboard():
    return render_template('home.html', username="Test")

if __name__ == "__main__":
    #serve(app, host="0.0.0.0", port=8000)
    app.run(host="0.0.0.0", port=8000, debug=True)