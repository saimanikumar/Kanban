
import os
basedir = os.path.abspath(os.path.dirname(__file__))

DB_NAME = "kanban.sqlite3"

class Config():
    DEBUG = True
    SQLITE_DB_DIR = os.path.join(basedir, "../db_directory")
    SQLALCHEMY_DATABASE_URI = "sqlite:///"+os.path.join(SQLITE_DB_DIR, DB_NAME)
    SECRET_KEY = 'ds@324Dfg5d12wsa!2q@$5'
