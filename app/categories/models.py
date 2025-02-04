from app import db

transaction_categories = db.Table(
    "transaction_categories",
    db.Column("transaction_id", db.Integer, db.ForeignKey("transaction.id"), primary_key=True),
    db.Column("category_id", db.Integer, db.ForeignKey("categories.id"), primary_key=True)
)

class Category(db.Model):
    __tablename__ = "categories"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    transactions = db.relationship("Transaction", secondary=transaction_categories, back_populates="categories")

    def to_dict(self):
        return {"id": self.id, "name": self.name}
