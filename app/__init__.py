from flask import Flask
import os

# from flask_mongoengine import MongoEngine, Document
# from flask_login import LoginManager
from .extensions import db, login_manager, cors
from .models.users import User

# Register Blueprint so we can factor routes
# from bmi import bmi, get_dict_from_csv, insert_reading_data_into_database

from .controllers.dashboard import dashboard
from .controllers.auth import auth
from .controllers.bookController import booking
from .controllers.packageController import package
from .controllers.api import api
from .routes import main

# import pymongo

def create_app():
    app = Flask(__name__)

    if os.getenv('SELF_TESTING') != '1':
        
        # Since both app and db are in the same container, we can use localhost
        # host = 'localhost' if os.getenv('FLASK_ENV') == 'development' else 'db'
        host = 'localhost' 
        
        app.config['MONGODB_SETTINGS'] = {
            'db': 'staycation',
            # 'host':'localhost' # choose this one when running locally
            # 'host':'db'      # choose this one when running as containers
            'host' : host
        }

        db.init_app(app)
    
    app.static_folder = 'assets'
    
    login_manager.init_app(app)
    cors.init_app(app)

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['DEBUG_TB_ENABLED'] = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    # app.config['SECRET_KEY'] = 'your_secret_key'
    # login_manager = LoginManager()
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please login or register first to get an account."
    # return app, db, login_manager
    # Load the current user if any
    @login_manager.user_loader
    def load_user(user_id):
        print('loading user_id: ', user_id)
        return User.getUserById(user_id)

    # register blueprint from respective module
    app.register_blueprint(dashboard)
    app.register_blueprint(auth)
    app.register_blueprint(booking)
    app.register_blueprint(package)
    app.register_blueprint(api)
    app.register_blueprint(main)

    @app.template_filter('formatdate') # use this name
    def format_date(value, format="%#d/%m/%Y"):
        """Format a date time to (Default): dd/mm/YYYY"""
        if value is None:
            return ""
        return value.strftime(format)

    @app.template_filter('formatmoney') # use this name
    def format_money(value, ndigits=2):
        """Format money with 2 decimal digits"""
        if value is None:
            return ""
        return f'{value:.{ndigits}f}'

    return app

# app, db, login_manager = create_app()

