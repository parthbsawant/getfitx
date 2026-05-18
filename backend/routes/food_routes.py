from flask import Blueprint

from controllers.food_controller import (
    add_food,
    get_today_foods,
    delete_food,
    get_dashboard_data,
    get_weekly_analytics
)


food_bp = Blueprint("food_bp", __name__)


# ADD FOOD
food_bp.route("/add", methods=["POST"])(add_food)
# GET TODAY'S FOODS
food_bp.route("/today/<user_id>", methods=["GET"])(get_today_foods)
# DELETE FOOD
food_bp.route("/delete/<food_id>", methods=["DELETE"])(delete_food)
# DASHBOARD DATA
food_bp.route("/dashboard/<user_id>", methods=["GET"])(get_dashboard_data)
# WEEKLY ANALYTICS
food_bp.route("/weekly/<user_id>",methods=["GET"])(get_weekly_analytics)