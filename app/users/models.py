from app import db, bcrypt

class User( db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    about_me = db.Column(db.String(500), nullable=True)  
   
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    def __init__(self, username, email, password, about_me  ):
        self.username = username
        self.email = email
        self.set_password(password)
        self.about_me = about_me 

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)