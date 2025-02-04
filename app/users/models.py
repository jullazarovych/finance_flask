from app import db, Bcrypt
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    about_me = db.Column(db.String(500), nullable=True)  
   
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = Bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return Bcrypt.check_password_hash(self.password_hash, password)