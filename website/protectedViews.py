from flask import Blueprint, Flask, render_template, request, flash, redirect
from flask_login import login_required, current_user
from sqlalchemy import func
from .authMethods import defense_againts_sql_attack_allow_space
from .models import User, Loan
from . import db

protectedViews = Blueprint('protectedViews', __name__)

@protectedViews.route('/home')
@login_required
def home():
    all_users_except_current = User.query.filter(User.id != current_user.id).all()

    users_and_owed_amount = []

    for user in all_users_except_current:
        total_owed_amount = (
            db.session.query(func.coalesce(func.sum(Loan.amount), 0))
            .filter(Loan.borrower_id == user.id, Loan.accepted.is_(True))
            .scalar()
        )

        users_and_owed_amount.append({'username': user.name, 'debt_amount': total_owed_amount})  
    
    return render_template('home.html', username=current_user.name, users=users_and_owed_amount)

@protectedViews.route('/loan', methods=['GET', 'POST'])
@login_required
def loan():
    if request.method == 'POST':
        borrower_name = request.form.get('username')
        purpose = request.form.get('purpose')
        amount = request.form.get('amount')
        
        onwer_user = User.query.filter_by(name=current_user.name).first()
        borrower_user = User.query.filter_by(name=borrower_name).first()
        
        if not (onwer_user and borrower_user):
            flash('Unfortunetly the system loged you out or the user you want to borrow mony does not exist. Try log out anf log in again and repeat the operation.', category='error')  
        elif not defense_againts_sql_attack_allow_space(purpose):
            flash('Purpose can\'t contains forbiden characters!', category='error')
        elif len(purpose) > 200:
            flash('Purpose have to contains maximum 200 characters!', category='error')
        elif int(amount) < 0:
            flash('The number of money you want to loan can\'t be nagative!', category='error')
        else:
            new_loan = Loan(
                amount=int(amount),
                purpose=purpose,
                accepted=False,  
                owner=onwer_user,
                borrower=borrower_user
            )

            db.session.add(new_loan)
            db.session.commit()
            flash('Loan added successfully!', 'success')
            
            return redirect(url_for('home'))
        
    all_user_names = [user.name for user in User.query.all() if user.name != current_user.name]
    
    return render_template('loan.html', user_names=all_user_names)

@protectedViews.route('/accept-request')
@login_required
def accept_request():
    user = User.query.filter_by(name=current_user.name).first()
    
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
    
    return render_template('accept-request.html', loan_requests=pending_loans)

@protectedViews.route('/pay', methods=['GET', 'POST'])
@login_required
def pay():
    all_user_names = [user.name for user in User.query.all() if user.name != current_user.name]
    
    return render_template('pay.html', user_names=all_user_names)