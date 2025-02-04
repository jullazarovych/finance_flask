from flask import request, jsonify
from flasgger import swag_from
from app import db
from app.users.models import User
from app.users import users_bp
@users_bp.route("/users", methods=["POST"])
@swag_from({
    "tags": ["Users"],
    "summary": "Create a new user",
    "description": "Creates a new user with a username, email, password, and optional about_me field.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "email": {"type": "string"},
                    "password": {"type": "string"},
                    "about_me": {"type": "string"}  
                },
                "required": ["username", "email", "password"]
            }
        }
    ],
    "responses": {
        "201": {"description": "User created successfully"},
        "400": {"description": "Email already exists"}
    }
})
def create_user():
    data = request.get_json()

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already exists"}), 400

    user = User(
        username=data["username"],
        email=data["email"],
        password=data["password"],  
        about_me=data.get("about_me", "")  
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User created successfully!",
        "user_id": user.id
    }), 201

@users_bp.route("/users", methods=["GET"])
@swag_from({
    "tags": ["Users"],
    "summary": "Get all users",
    "description": "Retrieves a list of all users.",
    "responses": {
        "200": {
            "description": "A list of users",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "username": {"type": "string"},
                        "email": {"type": "string"},
                        "about_me": {"type": "string"}
                    }
                }
            }
        }
    }
})
def get_users():
    users = User.query.all()
    return jsonify([
        {"id": user.id, "username": user.username, "email": user.email, "about_me": user.about_me}
        for user in users
    ])


@users_bp.route("/users/<int:user_id>", methods=["GET"])
@swag_from({
    "tags": ["Users"],
    "summary": "Get user by ID",
    "description": "Retrieves a user based on their ID.",
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "User ID"
        }
    ],
    "responses": {
        "200": {
            "description": "User details",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "username": {"type": "string"},
                    "email": {"type": "string"},
                    "about_me": {"type": "string"}
                }
            }
        },
        "404": {"description": "User not found"}
    }
})
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "about_me": user.about_me
    })


@users_bp.route("/users/<int:user_id>", methods=["PUT"])
@swag_from({
    "tags": ["Users"],
    "summary": "Update user by ID",
    "description": "Updates the details of an existing user.",
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "User ID"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "email": {"type": "string"},
                    "about_me": {"type": "string"},
                    "password": {"type": "string"}
                }
            }
        }
    ],
    "responses": {
        "200": {"description": "User updated successfully"},
        "400": {"description": "Email already exists"},
        "404": {"description": "User not found"}
    }
})
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()

    if "username" in data:
        user.username = data["username"]
    if "email" in data:
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"message": "Email already exists"}), 400
        user.email = data["email"]
    if "about_me" in data:
        user.about_me = data["about_me"]
    if "password" in data:
        user.password_hash = data["password"]

    db.session.commit()
    return jsonify({"message": "User updated successfully!"})


@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
@swag_from({
    "tags": ["Users"],
    "summary": "Delete user by ID",
    "description": "Deletes a user from the database.",
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "User ID"
        }
    ],
    "responses": {
        "200": {"description": "User deleted successfully"},
        "404": {"description": "User not found"}
    }
})
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully!"})
