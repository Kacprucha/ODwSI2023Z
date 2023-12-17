from flask import Blueprint, Flask, render_template, request, flash
from .authMethods import is_str_complex

authViews = Blueprint('authViews', __name__)

@authViews.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@authViews.route('/reset')
def forget_password():
    return render_template('reset_password.html')

@authViews.route('/register', methods=['GET', 'POST'])
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
            
    return render_template('register.html')