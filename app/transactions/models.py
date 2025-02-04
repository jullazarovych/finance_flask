from app import db
from datetime import datetime
from app.categories.models import Category
from app.categories.models import transaction_categories
user_transaction = db.Table(
    "user_transaction",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("transaction_id", db.Integer, db.ForeignKey("transactions.id"), primary_key=True)
)

class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.Enum("expense", "revenue", name="transaction_type"), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship("User", secondary=user_transaction, backref=db.backref("transactions", lazy="dynamic"))
    categories = db.relationship("Category", secondary=transaction_categories, back_populates="transactions")

    def __init__(self, amount, type, description=None, date=None, categories=None):
        self.amount = amount
        self.type = type
        self.description = description
        self.date = date if date else datetime.utcnow() 
        if categories:
            self.categories = categories