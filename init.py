import datetime
from flask import Flask, redirect, url_for, render_template, request, redirect, session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.secret_key = "Access Control"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    db.init_app(app)

    from views import views

    app.register_blueprint(views, url_prefix='/')
    from models import User

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


    
    db.create_all(app=app)

    

    return app

    