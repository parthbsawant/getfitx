from flask import Blueprint
from controllers.analytics_controller import (
    get_calorie_analysis,
    get_fat_loss_analysis,
    get_meal_distribution_analysis,
    get_insights,
    get_macros
)

analytics_bp = Blueprint("analytics_bp", __name__)

analytics_bp.route("/calories/<user_id>", methods=["GET"])(get_calorie_analysis)
analytics_bp.route("/fat-loss/<user_id>", methods=["GET"])(get_fat_loss_analysis)
analytics_bp.route("/meal-distribution/<user_id>", methods=["GET"])(get_meal_distribution_analysis)
analytics_bp.route("/insights/<user_id>", methods=["GET"])(get_insights)
analytics_bp.route("/macros/<user_id>", methods=["GET"])(get_macros)
