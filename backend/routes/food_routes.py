from flask import Blueprint

from controllers.food_controller import add_food


food_bp = Blueprint("food_bp", __name__)


# ADD FOOD
food_bp.route("/add", methods=["POST"])(add_food)