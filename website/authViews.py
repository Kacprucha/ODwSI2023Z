from flask import Blueprint, Flask, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.sql import func
from .authMethods import is_str_complex, hash_password, generate_random_salt, generate_code, verify_password, defense_againts_sql_attack
from .models import User, Loan
from . import db
import time

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
            
            time.sleep(2.3)
            
            if verify_password(password, db_password, salt):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                
                pending_loans = db.session.query(
                        User.name.label('user_name'),
                        Loan.amount,
                        Loan.purpose
                    ).join(
                        Loan, 
                        Loan.owner_id == User.id
                    ).filter(
                        Loan.borrower_id == user.id, 
                        Loan.accepted.is_(False)
                    ).all()
                
                if len(pending_loans) > 0:
                    flash(f"You have {len(pending_loans)} awaiting requests.")
                
                if user.loans_accepted_when_last_loged < Loan.query.filter_by(owner=user, accepted=True).count():
                    flash(f"You have {Loan.query.filter_by(owner=user, accepted=True).count() - user.loans_accepted_when_last_loged} accepted loan(s).", category='sucesses')
                
                if user.all_loans_when_last_loged > len(user.loans_as_owner):
                    flash(f"You have {user.all_loans_when_last_loged - len(user.loans_as_owner)} decline loan(s).", category='error')
                    
                return redirect(url_for('protectedViews.home'))
            else:
                flash('Login error!', category='error')
        else:
            flash('Login error', category='error')
            
    return render_template('login.html')

@authViews.route('/logout')
@login_required
def logout():
    user = User.query.filter_by(name=current_user.name).first()
    user.loans_accepted_when_last_loged = Loan.query.filter_by(owner=user, accepted=True).count()
    user.all_loans_when_last_loged = len(user.loans_as_owner)
    db.session.commit()
    
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
            flash('Reset password error!', category='error')
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
                    user.password_date_change=func.now()
                    db.session.commit()
                    
                    login_user(user, remember=True)
                    flash('Password changed!', category='sucesses')
                    flash(f"Your new code for resetting password {code_nh}. Write it down !!!", category='warning')
                    return redirect(url_for('protectedViews.home'))
            else:
                flash('Reset password error!', category='error')
                    
                
    return render_template('reset_password.html', forget_password=True)

@authViews.route('/change_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    if request.method == 'POST':
        code = request.form.get('code')
        password1 = request.form.get('new_password')
        password2 = request.form.get('confirm_password')
        
        user = User.query.filter_by(name=current_user.name).first()
        if not user:
            flash('Reset password error!', category='error')
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
                    user.password_date_change=func.now()
                    db.session.commit()
                    
                    login_user(user, remember=True)
                    flash('Password changed!', category='sucesses')
                    flash(f"Your new code for resetting password {code_nh}. Write it down !!!", category='warning')
                    return redirect(url_for('protectedViews.home'))
            else:
                flash('Reset password error!', category='error')
                    
                
    return render_template('reset_password.html', forget_password=False)

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
        elif len(username) > 150:
            flesh('Username must be less then 150 characters.', category='error')
        elif not defense_againts_sql_attack(username):
            flesh('Username can\'t contains forbiden characters or spaces!', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif not is_str_complex(password1):
            flash('Password must be at least 8 characters long, has at least one number, has at least one special character and has at least one capital letter.', category='error')
        elif len(password1) > 150:
            flash('Password must be less then 150 characters.', category='error')
        elif not defense_againts_sql_attack(password1):
            flash('Password can\'t contains forbide characters or spaces!', category='error')
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