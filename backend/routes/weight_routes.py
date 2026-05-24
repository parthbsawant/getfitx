from flask import Blueprint

from controllers.weight_controller import (
    add_weight,
    get_weight_history,
    get_weight_analytics
)

weight_bp = Blueprint(
    "weight_bp",
    __name__
)

# ADD WEIGHT
weight_bp.route(
    "/add",
    methods=["POST"]
)(add_weight)

# GET WEIGHT HISTORY
weight_bp.route(
    "/history/<user_id>",
    methods=["GET"]
)(get_weight_history)

# WEIGHT ANALYTICS
weight_bp.route(
    "/analytics/<user_id>",
    methods=["GET"]
)(get_weight_analytics)