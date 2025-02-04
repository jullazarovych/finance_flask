from flask import Blueprint

users_bp=Blueprint("user_name", __name__, url_prefix="/api")
from . import view
