from flask import Blueprint
from controllers.exercise_controller import (
    add_exercise,
    get_today_exercise,
    get_exercise_history,
    delete_exercise
)

exercise_bp = Blueprint("exercise_bp", __name__)

exercise_bp.route("/add", methods=["POST"])(add_exercise)
exercise_bp.route("/today/<user_id>", methods=["GET"])(get_today_exercise)
exercise_bp.route("/history/<user_id>", methods=["GET"])(get_exercise_history)
exercise_bp.route("/delete/<log_id>", methods=["DELETE"])(delete_exercise)
