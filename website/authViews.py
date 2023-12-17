from flask import Blueprint, Flask, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .authMethods import is_str_complex, hash_password, generate_random_salt, generate_code, verify_password
from .models import User
from . import db

authViews = Blueprint('authViews', __name__)

@authViews.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(name=username).first()
        if user:
            salt = user.password[:8]
            db_password = user.password[8:]
            print(user.password)
            print(salt)
            print(db_password)
            if verify_password(password, db_password, salt):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('protectedViews.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Username does not exist.', category='error')
            
    return render_template('login.html')

@authViews.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('generalViews.index'))

@authViews.route('/reset')
def forget_password():
    return render_template('reset_password.html')

@authViews.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password1 = request.form.get('password')
        password2 = request.form.get('confirm_password')

        user = User.query.filter_by(name=username).first()
        if user:
            flash('User of that username already exists.', category='error')
        elif len(username) < 4:
            flash('Username must be greater than 3 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif not is_str_complex(password1):
            flash('Password must be at least 8 characters long, has at least one number, has at least one special character and has at least one capital letter.', category='error')
        else:
            salt = generate_random_salt(8)
            password = hash_password(password1, salt)
            password = salt + password
            code = hash_password(generate_code(8), salt)
            
            new_user = User(name=username, password=password, code=code)
            db.session.add(new_user)
            db.session.commit()
            login_user(user, remember=True)
            flash('Account created!', category='sucesses')
            return redirect(url_for('protectedViews.home'))
            
    return render_template('register.html')