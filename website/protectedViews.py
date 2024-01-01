from flask import Blueprint, Flask, render_template, request, flash
from flask_login import login_required, current_user

protectedViews = Blueprint('protectedViews', __name__)

@protectedViews.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    return render_template('home.html', username=current_user.name)