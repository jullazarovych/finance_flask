from flask import Flask

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
migrate = Migrate() 
bcrypt = Bcrypt()

def create_app(config_name="config"):
    app = Flask(__name__)
    app.config.from_object(config_name)  
    bcrypt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        from .view import main_bp 
        app.register_blueprint(main_bp)
        
        from app.users.models import User
        from app.users import users_bp
        app.register_blueprint(users_bp, url_prefix="/api")
        
        from app.transactions.models import Transaction
        from app.transactions import transactions_bp
        app.register_blueprint(transactions_bp, url_prefix="/api")
        
        from app.categories.models import Category
        from app.categories import categories_bp
        app.register_blueprint(categories_bp, url_prefix="/api")
        
        Swagger(app)
    return app

