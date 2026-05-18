from flask import Blueprint
from controllers.goal_controller import set_goal

goal_bp = Blueprint('goal_bp', __name__)

goal_bp.route('/set-goal', methods=['POST'])(set_goal)