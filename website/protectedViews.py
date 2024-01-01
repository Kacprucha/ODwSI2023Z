from flask import Blueprint, Flask, render_template, request, flash
from flask_login import login_required, current_user

protectedViews = Blueprint('protectedViews', __name__)

@protectedViews.route('/home')
@login_required
def home():
    return render_template('home.html', username=current_user.name)

@protectedViews.route('/loan', methods=['GET', 'POST'])
@login_required
def loan():
    return render_template('loan.html')

@protectedViews.route('/pay', methods=['GET', 'POST'])
@login_required
def pay():
    return render_template('pay.html')