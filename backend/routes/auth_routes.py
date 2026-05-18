from flask import Blueprint
from controllers.auth_controller import (
    signup,
    login,
    get_profile
)

auth_bp = Blueprint('auth_bp', __name__)

auth_bp.route('/signup', methods=['POST'])(signup)
auth_bp.route('/login', methods=['POST'])(login)
auth_bp.route('/profile', methods=['GET'])(get_profile)