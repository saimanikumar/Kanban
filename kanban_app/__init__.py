from flask import Flask
import os
from os import path
from flask_login import LoginManager
from .config import Config
import matplotlib
import matplotlib.pyplot as plt
from flask_restful import Api
from .model import User
from .database import db

api = None

DB_NAME = "kanban.sqlite3"


def create_app():
    
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(Config)
    db.init_app(app)
    api = Api(app)
    app.app_context().push()

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')


    create_database(app)
    from .model import User

    login_manager = LoginManager()
    login_manager.login = 'auth.login'
    login_manager.init_app(app)


    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))    
    

    matplotlib.use("Agg")


    return app, api



def create_database(app):
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLITE_DB_DIR = os.path.join(basedir, "../db_directory")
    
    if not path.exists(SQLITE_DB_DIR + DB_NAME):
        db.create_all(app=app)
