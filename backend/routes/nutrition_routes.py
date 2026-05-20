from flask import Blueprint

from controllers.nutrition_controller import (
    search_foods
)

nutrition_bp = Blueprint(
    "nutrition_bp",
    __name__
)


# SEARCH FOODS
nutrition_bp.route(
    "/search",
    methods=["GET"]
)(search_foods)