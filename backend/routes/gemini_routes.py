from flask import Blueprint

from controllers.gemini_controller import (
    ai_food_estimation
)

gemini_bp = Blueprint(
    "gemini_bp",
    __name__
)


# AI FOOD ESTIMATION
gemini_bp.route(
    "/estimate",
    methods=["POST"]
)(ai_food_estimation)