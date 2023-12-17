from flask import Blueprint, Flask, render_template, request, flash

generalViews = Blueprint('generalViews', __name__)

@generalViews.route('/')
@generalViews.route('/index')
def index():
    return render_template('index.html')