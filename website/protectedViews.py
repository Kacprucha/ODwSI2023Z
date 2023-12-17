from flask import Blueprint, Flask, render_template, request, flash

protectedViews = Blueprint('protectedViews', __name__)

@protectedViews.route('/home')
def dashboard():
    return render_template('home.html', username="Test")