from flask import Blueprint, Flask, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .authMethods import is_str_complex, hash_password, generate_random_salt, generate_code, verify_password, defense_againts_sql_attack
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

@authViews.route('/reset', methods=['GET', 'POST'])
def forget_password():
    if request.method == 'POST':
        username = request.form.get('username')
        code = request.form.get('code')
        password1 = request.form.get('new_password')
        password2 = request.form.get('confirm_password')
        
        user = User.query.filter_by(name=username).first()
        if not user:
            flash('User of that username doesn\'t exists.', category='error')
        else:
            salt = user.password[:8]
            user_code = user.code
            
            if verify_password(code, user_code, salt):
                if password1 != password2:
                    flash('Passwords don\'t match.', category='error')
                elif not is_str_complex(password1):
                    flash('Password must be at least 8 characters long, has at least one number, has at least one special character and has at least one capital letter.', category='error')
                else:
                    password = hash_password(password1, salt)
                    password = salt + password
                    code_nh = generate_code(8)
                    new_code = hash_password(code_nh, salt)
                    
                    user.password = password
                    user.code = new_code
                    db.session.commit()
                    
                    login_user(user, remember=True)
                    flash('Password changed!', category='sucesses')
                    flash(f"Your new code for resetting password {code_nh}. Write it down !!!", category='warning')
                    return redirect(url_for('protectedViews.home'))
            else:
                flash('The code is incorrect!', category='error')
                    
                
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
        elif not defense_againts_sql_attack(username):
            flash('Username can\'t contains characters like: `;=- or spaces!', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif not is_str_complex(password1):
            flash('Password must be at least 8 characters long, has at least one number, has at least one special character and has at least one capital letter.', category='error')
        elif not defense_againts_sql_attack(password1):
            flash('Password can\'t contains characters like: `;=- or spaces!', category='error')
        else:
            salt = generate_random_salt(8)
            password = hash_password(password1, salt)
            password = salt + password
            code_nh = generate_code(8)
            code = hash_password(code_nh, salt)
            
            new_user = User(name=username, password=password, code=code)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='sucesses')
            flash(f"Your code for resetting password {code_nh}. Write it down !!!", category='warning')
            return redirect(url_for('protectedViews.home'))
            
    return render_template('register.html')