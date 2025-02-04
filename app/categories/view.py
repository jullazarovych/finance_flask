from flask import Blueprint, request, jsonify
from flasgger import swag_from
from app import db
from app.categories.models import Category 
from app.categories import categories_bp

@categories_bp.route("/categories", methods=["POST"])
@swag_from({
    "tags": ["Categories"],
    "summary": "Create a new category",
    "parameters": [
        {"name": "body", "in": "body", "schema": {"type": "object", "properties": {"name": {"type": "string"}}}}
    ],
    "responses": {
        "201": {"description": "Category created"},
        "400": {"description": "Category already exists"}
    }
})
def create_category():
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"message": "Category name is required"}), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({"message": "Category already exists"}), 400

    category = Category(name=name)
    db.session.add(category)
    db.session.commit()

    return jsonify({"message": "Category created!", "category": category.to_dict()}), 201


@categories_bp.route("/categories", methods=["GET"])
@swag_from({
    "tags": ["Categories"],
    "summary": "Get all categories",
    "responses": {"200": {"description": "List of categories"}}
})
def get_categories():
    categories = Category.query.all()
    return jsonify([category.to_dict() for category in categories])


@categories_bp.route("/categories/<int:category_id>", methods=["GET"])
@swag_from({
    "tags": ["Categories"],
    "summary": "Get a category by ID",
    "parameters": [
        {
            "name": "category_id", 
            "in": "path", 
            "required": True, 
            "type": "integer"
        }
    ],
    "responses": {
        "200": {"description": "Category found", "schema": {"type": "object", "properties": {"id": {"type": "integer"}, "name": {"type": "string"}}}},
        "404": {"description": "Category not found"}
    }
})
def get_category_by_id(category_id):
    category = Category.query.get(category_id)
    
    if not category:
        return jsonify({"message": "Category not found"}), 404
    
    return jsonify(category.to_dict())

@categories_bp.route("/categories/<int:category_id>", methods=["PUT"])
@swag_from({
    "tags": ["Categories"],
    "summary": "Update a category",
    "parameters": [
        {"name": "category_id", "in": "path", "required": True, "type": "integer"},
        {"name": "body", "in": "body", "schema": {"type": "object", "properties": {"name": {"type": "string"}}}}
    ],
    "responses": {"200": {"description": "Category updated"}, "404": {"description": "Category not found"}}
})
def update_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"message": "Category not found"}), 404

    data = request.get_json()
    category.name = data.get("name", category.name)

    db.session.commit()
    return jsonify({"message": "Category updated!", "category": category.to_dict()})


@categories_bp.route("/categories/<int:category_id>", methods=["DELETE"])
@swag_from({
    "tags": ["Categories"],
    "summary": "Delete a category",
    "parameters": [{"name": "category_id", "in": "path", "required": True, "type": "integer"}],
    "responses": {"200": {"description": "Category deleted"}, "404": {"description": "Category not found"}}
})
def delete_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"message": "Category not found"}), 404

    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted!"})
