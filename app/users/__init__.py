from flask import Blueprint

users_bp=Blueprint("user_name", __name__)
from . import view
