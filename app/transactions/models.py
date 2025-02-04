from app import db
from datetime import datetime

user_transaction = db.Table(
    "user_transaction",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("transaction_id", db.Integer, db.ForeignKey("transaction.id"), primary_key=True)
)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False) 
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship("User", secondary=user_transaction, backref=db.backref("transactions", lazy="dynamic"))

    def __init__(self, amount, type, category, description=None):
        self.amount = amount
        self.type = type
        self.category = category
        self.description = description