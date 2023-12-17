from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
db_name = os.getenv("DB_NAME")
secret_key = os.getenv("SECRET_KEY")

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_name}'
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
        
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app