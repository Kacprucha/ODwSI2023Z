from flask import Blueprint, Flask, render_template, request, flash, redirect, jsonify, url_for
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime
from .authMethods import defense_againts_sql_attack_allow_space
from .models import User, Loan
from . import db
import json

protectedViews = Blueprint('protectedViews', __name__)
global _loan_to_pay

@protectedViews.route('/home')
@login_required
def home():
    all_users_except_current = User.query.filter(User.id != current_user.id).all()

    users_and_owed_amount = []

    for user in all_users_except_current:
        total_owed_amount = (
            db.session.query(func.coalesce(func.sum(Loan.amount), 0))
            .filter(Loan.owner_id == user.id, Loan.accepted.is_(True))
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
        date = request.form.get('dateToPay')
        date_object = datetime.strptime(date, '%Y-%m-%d')
        
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
                date=date_object,  
                owner=onwer_user,
                borrower=borrower_user
            )

            db.session.add(new_loan)
            db.session.commit()
            flash('Loan added successfully!', 'success')
            
            return redirect(url_for('protectedViews.home'))
        
    all_user_names = [user.name for user in User.query.all() if user.name != current_user.name]
    
    return render_template('loan.html', user_names=all_user_names)

@protectedViews.route('/accept-request')
@login_required
def accept_request():
    user = User.query.filter_by(name=current_user.name).first()
    
    pending_loans = db.session.query(
            User.name.label('user_name'),
            Loan.amount,
            Loan.purpose,
            Loan.id,
            Loan.date
        ).join(
            Loan, 
            Loan.owner_id == User.id
        ).filter(
            Loan.borrower_id == user.id, 
            Loan.accepted.is_(False)
        ).all() 
    
    return render_template('accept-request.html', loan_requests=pending_loans)

@protectedViews.route('/choose-loan', methods=['GET', 'POST'])
@login_required
def choose_loan():
    user = User.query.filter_by(name=current_user.name).first()
    
    accepted_loans = (
        Loan.query.filter_by(owner=user, accepted=True)
        .all()
    )
    
    return render_template('choose-loan.html', loans=accepted_loans)

@protectedViews.route('/pay', methods=['GET', 'POST'])
@login_required
def pay():
    global _loan_to_pay
    
    if request.method == 'GET':
        loan_id = request.args.get("selectedLoans")
        _loan_to_pay = Loan.query.get(loan_id)
        
    if request.method == 'POST':
        amount_want_to_pay = request.form.get('amount')
        amount_to_pay = _loan_to_pay.amount
        
        if int(amount_want_to_pay) > int(amount_to_pay):
            flash('The loan in less then what you want to pay!', category='error')
        else:
            loan = Loan.query.get(_loan_to_pay.id)
            loan.amount = int(amount_to_pay) - int(amount_want_to_pay)
            db.session.commit()
            
            if loan.amount == 0:
                db.session.delete(loan)
                db.session.commit()
                _loan_to_pay = Loan()
                
                flash('Congrats you pay your loan!', category='success')
                
            return redirect(url_for('protectedViews.home'))   
    
    return render_template('pay.html', loan_to_pay=_loan_to_pay)

@protectedViews.route('/accept-loan', methods=['POST'])
@login_required
def accept_loan():  
    loan_jason = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    loan_id = loan_jason['loanId']
    loan = Loan.query.get(loan_id)
    
    if loan and loan.borrower_id == current_user.id:
        loan.accepted = True
        db.session.commit()

    return jsonify({})

@protectedViews.route('/decline-loan', methods=['POST'])
@login_required
def decline_loan():  
    loan_jason = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    loan_id = loan_jason['loanId']
    loan = Loan.query.get(loan_id)
    
    if loan and loan.borrower_id == current_user.id:
        db.session.delete(loan)
        db.session.commit()

    return jsonify({})

@protectedViews.route('/accepted-loans')
@login_required
def accept_loans():
    user = User.query.filter_by(name=current_user.name).first()
    
    accepted_loans = (
        Loan.query.filter_by(owner=user, accepted=True)
        .all()
    ) 
    
    return render_template('accepted-loans.html', user_loans=accepted_loans)

@protectedViews.route('/accepted-borrows')
@login_required
def accept_borrows():
    user = User.query.filter_by(name=current_user.name).first()
    
    accepted_borrows = (
        Loan.query.filter_by(borrower=user, accepted=True)
        .all()
    ) 
    
    return render_template('accepted-borrows.html', user_borrows=accepted_borrows)

@protectedViews.route('/user-settings')
@login_required
def user_settings():
    user = User.query.filter_by(name=current_user.name).first()
    
    return render_template('user-settings.html', username=user.name, last_password_change=func.now())