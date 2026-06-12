from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from app.admin import admin

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app import models
    from app.routes import home
    from app.auth import auth


    app.register_blueprint(home)
    app.register_blueprint(auth)
    app.register_blueprint(admin)

    return app