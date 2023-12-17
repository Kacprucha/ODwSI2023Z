from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    
    from .authViews import authViews
    from .generalViews import generalViews
    from .protectedViews import protectedViews
    
    app.register_blueprint(generalViews, url_prefix='/')
    app.register_blueprint(authViews, url_prefix='/')
    app.register_blueprint(protectedViews, url_prefix='/')
    
    from .models import User, Loan
    
    with app.app_context():
        db.create_all()
    
    return app