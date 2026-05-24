from flask import request, jsonify

from services.gemini_service import (
    estimate_food_nutrition
)


def ai_food_estimation():

    try:

        data = request.get_json()

        user_input = data.get("query")

        if not user_input:

            return jsonify({
                "success": False,
                "message": "Query required"
            }), 400

        result = estimate_food_nutrition(
            user_input
        )

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500