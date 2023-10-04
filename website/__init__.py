from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail


db = SQLAlchemy()
DB_NAME = 'database.db'
mail = Mail()



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'organico'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = "souranshus@gmail.com"
    app.config["MAIL_PASSWORD"] = "qhbd nsnm auhn kenz"
    db.init_app(app)
    mail.init_app(app)
    
    
    from .views import views
    from .auth import auth
    
    
    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')
    
    from .models import User
    create_database(app)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        
        print('Created Database')

