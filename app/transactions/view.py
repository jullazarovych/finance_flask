from flask import request, jsonify
from flasgger import swag_from
from app import db
from sqlalchemy import func
from app.users.models import User
from app.transactions.models import Transaction, transaction_categories, user_transaction
from datetime import datetime, timedelta
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

    valid_types = {"expense", "revenue"}
    transaction_type = data.get("type")
    if transaction_type not in valid_types:
        return jsonify({"message": "Invalid transaction type. Allowed values: 'expense', 'revenue'"}), 400

    categories = Category.query.filter(Category.name.in_(categories_data)).all()
    if not categories:
        return jsonify({"message": "Invalid categories provided"}), 400

    users = User.query.filter(User.id.in_(user_ids)).all()
    if not users:
        return jsonify({"message": "No valid users found"}), 400

    transaction = Transaction(
        amount=data["amount"],
        type=transaction_type,
        description=data.get("description", "")
    )

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
        "400": {"description": "Invalid transaction type"},
        "404": {"description": "Transaction not found"}
    }
})
def update_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({"message": "Transaction not found"}), 404

    data = request.get_json()

    valid_types = {"expense", "revenue"}
    if "type" in data and data["type"] not in valid_types:
        return jsonify({"message": "Invalid transaction type. Allowed values: 'expense', 'revenue'"}), 400

    transaction.amount = data.get("amount", transaction.amount)
    transaction.type = data.get("type", transaction.type)
    transaction.description = data.get("description", transaction.description)

    categories_data = data.get("categories", [])
    if categories_data:
        categories = Category.query.filter(Category.name.in_(categories_data)).all()
        transaction.categories = categories

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

@transactions_bp.route("/reports/monthly_expenses", methods=["POST"])
@swag_from({
    "tags": ["Reports"],
    "summary": "Get monthly transactions report filtered by type and category",
    "description": "This endpoint returns the total amounts for a given month, grouped by category. Can be filtered by transaction type and specific category.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "month": {
                        "type": "string",
                        "description": "The month for which transactions need to be calculated. Format: YYYY-MM",
                        "example": "2025-02"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "The ID of the user whose transactions need to be calculated",
                        "example": 1
                    },
                    "type": {
                        "type": "string",
                        "description": "Transaction type filter (expense/revenue). If not provided, all types will be included",
                        "enum": ["expense", "revenue"],
                        "example": "expense"
                    },
                    "category": {
                        "type": "string",
                        "description": "Category name to filter by. If not provided, all categories will be included",
                        "example": "food"
                    }
                },
                "required": ["month", "user_id"]
            }
        }
    ],
    "responses": {
        "200": {
            "description": "List of total amounts grouped by category",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "The name of the category"
                        },
                        "total_amount": {
                            "type": "number",
                            "description": "The total amount for this category"
                        }
                    }
                }
            }
        },
        "400": {
            "description": "Invalid input parameters"
        },
        "404": {
            "description": "User not found"
        }
    }
})
def monthly_expenses():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body is required"}), 400

    month = data.get("month")
    if not month:
        return jsonify({"message": "Month parameter is required"}), 400

    user_id = data.get("user_id")
    if user_id is None:
        return jsonify({"message": "User ID parameter is required"}), 400

    transaction_type = data.get("type")
    category_name = data.get("category")

    if transaction_type and transaction_type not in ['expense', 'revenue']:
        return jsonify({"message": "Invalid transaction type. Must be 'expense' or 'revenue'"}), 400

    try:
        month_start = datetime.strptime(month, "%Y-%m")
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1)
        month_end = month_end - timedelta(microseconds=1)
        
    except ValueError as e:
        return jsonify({"message": "Invalid month format"}), 400
    try:
        query = db.session.query(
            Category.name,
            func.sum(Transaction.amount).label('total_amount')
        ).join(
            transaction_categories,
            Transaction.id == transaction_categories.c.transaction_id
        ).join(
            Category,
            Category.id == transaction_categories.c.category_id
        ).join(
            user_transaction,
            Transaction.id == user_transaction.c.transaction_id
        ).filter(
            Transaction.date >= month_start,
            Transaction.date <= month_end,
            user_transaction.c.user_id == user_id
        )

        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)

        if category_name:
            query = query.filter(Category.name == category_name)

        query = query.group_by(Category.name)

        transactions = query.all()
        result = [{
            "category": transaction[0],
            "total_amount": float(transaction[1]) if transaction[1] is not None else 0
        } for transaction in transactions]

        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "message": "Internal server error",
            "error": str(e)
        }), 500