from flask import Blueprint, jsonify, request

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def main():
    return jsonify({"message": "Welcome!"})

@main_bp.route('/homepage')
def home():
    agent = request.user_agent.string
    return jsonify({"user_agent": agent})

