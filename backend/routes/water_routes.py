from flask import Blueprint
from controllers.water_controller import (
    add_water,
    get_today_water,
    get_water_history,
    delete_water,
    set_water_goal
)

water_bp = Blueprint("water_bp", __name__)

water_bp.route("/add", methods=["POST"])(add_water)
water_bp.route("/today/<user_id>", methods=["GET"])(get_today_water)
water_bp.route("/history/<user_id>", methods=["GET"])(get_water_history)
water_bp.route("/delete/<log_id>", methods=["DELETE"])(delete_water)
water_bp.route("/goal", methods=["POST"])(set_water_goal)
