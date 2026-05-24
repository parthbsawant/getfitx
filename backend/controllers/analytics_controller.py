from flask import jsonify
from services.analytics_service import (
    get_calorie_analytics,
    get_fat_loss_analytics,
    get_meal_distribution_analytics,
    get_macro_analytics
)
from services.insight_service import generate_coaching_insights

def get_calorie_analysis(user_id):
    try:
        data = get_calorie_analytics(user_id)
        return jsonify({
            "success": True,
            **data
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

def get_fat_loss_analysis(user_id):
    try:
        data = get_fat_loss_analytics(user_id)
        return jsonify({
            "success": True,
            "fatLossEstimation": data
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

def get_meal_distribution_analysis(user_id):
    try:
        data = get_meal_distribution_analytics(user_id)
        return jsonify({
            "success": True,
            **data
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

def get_insights(user_id):
    try:
        data = generate_coaching_insights(user_id)
        return jsonify({
            "success": True,
            "insights": data
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

def get_macros(user_id):
    try:
        data = get_macro_analytics(user_id)
        return jsonify({
            "success": True,
            "macros": data
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
