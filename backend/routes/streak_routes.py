from flask import Blueprint
from controllers.streak_controller import (
    get_advanced_streak,
    freeze_streak,
    grant_freezes
)

streak_bp = Blueprint("streak_bp", __name__)

streak_bp.route("/advanced/<user_id>", methods=["GET"])(get_advanced_streak)
streak_bp.route("/freeze", methods=["POST"])(freeze_streak)
streak_bp.route("/add-freeze", methods=["POST"])(grant_freezes)
