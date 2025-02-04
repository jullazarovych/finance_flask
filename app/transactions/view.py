from flask import request, jsonify
from flasgger import swag_from
from app import db
from app.users.models import User
from app.transactions.models import Transaction
from app.transactions import transactions_bp
from app.categories.models import Category

@transactions_bp.route("/transactions", methods=["POST"])
@swag_from({
    "tags": ["Transactions"],
    "summary": "Create a new transaction",
    "description": "Creates a new transaction and associates it with users",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "type": {"type": "string"},
                    "categories": {"type": "array", "items": {"type": "string"}},
                    "description": {"type": "string"},
                    "user_ids": {"type": "array", "items": {"type": "integer"}}
                },
                "required": ["amount", "type", "categories", "user_ids"]
            }
        }
    ],
    "responses": {
        "201": {"description": "Transaction created successfully"},
        "400": {"description": "Invalid request"}
    }
})
def create_transaction():
    data = request.get_json()

    user_ids = data.get("user_ids", [])
    if not user_ids:
        return jsonify({"message": "At least one user is required"}), 400

    categories_data = data.get("categories", [])
    if not categories_data:
        return jsonify({"message": "At least one category is required"}), 400

    # Fetch categories from the database
    categories = Category.query.filter(Category.name.in_(categories_data)).all()
    if not categories:
        return jsonify({"message": "Invalid categories provided"}), 400

    transaction = Transaction(
        amount=data["amount"],
        type=data["type"],
        description=data.get("description", "")
    )

    users = User.query.filter(User.id.in_(user_ids)).all()
    if not users:
        return jsonify({"message": "No valid users found"}), 400

    transaction.users.extend(users)
    transaction.categories.extend(categories)

    db.session.add(transaction)
    db.session.commit()

    return jsonify({"message": "Transaction created!", "transaction_id": transaction.id}), 201


@transactions_bp.route("/transactions", methods=["GET"])
@swag_from({
    "tags": ["Transactions"],
    "summary": "Get all transactions",
    "description": "Retrieves all transactions with details",
    "responses": {
        "200": {
            "description": "List of transactions",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "amount": {"type": "number"},
                        "type": {"type": "string"},
                        "categories": {"type": "array", "items": {"type": "string"}},
                        "description": {"type": "string"},
                        "date": {"type": "string"},
                        "users": {"type": "array", "items": {"type": "integer"}}
                    }
                }
            }
        }
    }
})
def get_transactions():
    transactions = Transaction.query.all()
    return jsonify([
        {
            "id": t.id,
            "amount": t.amount,
            "type": t.type,
            "categories": [category.name for category in t.categories],
            "description": t.description,
            "date": t.date.isoformat(),
            "users": [u.id for u in t.users]
        }
        for t in transactions
    ])


@transactions_bp.route("/transactions/<int:transaction_id>", methods=["GET"])
@swag_from({
    "tags": ["Transactions"],
    "summary": "Get a transaction by ID",
    "description": "Retrieves a specific transaction using its ID",
    "parameters": [
        {"name": "transaction_id", "in": "path", "required": True, "type": "integer"}
    ],
    "responses": {
        "200": {"description": "Transaction found"},
        "404": {"description": "Transaction not found"}
    }
})
def get_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({"message": "Transaction not found"}), 404

    return jsonify({
        "id": transaction.id,
        "amount": transaction.amount,
        "type": transaction.type,
        "categories": [category.name for category in transaction.categories],
        "description": transaction.description,
        "date": transaction.date.isoformat(),
        "users": [user.id for user in transaction.users]
    })


@transactions_bp.route("/transactions/<int:transaction_id>", methods=["PUT"])
@swag_from({
    "tags": ["Transactions"],
    "summary": "Update a transaction",
    "description": "Updates an existing transaction by ID",
    "parameters": [
        {"name": "transaction_id", "in": "path", "required": True, "type": "integer"},
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "type": {"type": "string"},
                    "categories": {"type": "array", "items": {"type": "string"}},
                    "description": {"type": "string"},
                    "user_ids": {"type": "array", "items": {"type": "integer"}}
                }
            }
        }
    ],
    "responses": {
        "200": {"description": "Transaction updated successfully"},
        "404": {"description": "Transaction not found"}
    }
})
def update_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({"message": "Transaction not found"}), 404

    data = request.get_json()

    transaction.amount = data.get("amount", transaction.amount)
    transaction.type = data.get("type", transaction.type)
    transaction.description = data.get("description", transaction.description)

    # Update categories
    categories_data = data.get("categories", [])
    if categories_data:
        categories = Category.query.filter(Category.name.in_(categories_data)).all()
        transaction.categories = categories

    # Update users
    user_ids = data.get("user_ids", [])
    if user_ids:
        users = User.query.filter(User.id.in_(user_ids)).all()
        transaction.users = users

    db.session.commit()
    return jsonify({"message": "Transaction updated!"})


@transactions_bp.route("/transactions/<int:transaction_id>", methods=["DELETE"])
@swag_from({
    "tags": ["Transactions"],
    "summary": "Delete a transaction",
    "description": "Deletes a specific transaction by ID",
    "parameters": [
        {"name": "transaction_id", "in": "path", "required": True, "type": "integer"}
    ],
    "responses": {
        "200": {"description": "Transaction deleted successfully"},
        "404": {"description": "Transaction not found"}
    }
})
def delete_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({"message": "Transaction not found"}), 404

    db.session.delete(transaction)
    db.session.commit()
    return jsonify({"message": "Transaction deleted!"})
