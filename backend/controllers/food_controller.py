from flask import request, jsonify
from datetime import datetime

from models.food_model import create_food_log


def add_food():

    try:

        data = request.get_json()

        food_data = {
            "userId": data.get("userId"),
            "foodName": data.get("foodName"),
            "calories": data.get("calories"),
            "protein": data.get("protein", 0),
            "carbs": data.get("carbs", 0),
            "fats": data.get("fats", 0),
            "quantity": data.get("quantity", ""),
            "mealType": data.get("mealType"),
            "consumedAt": datetime.utcnow()
        }

        result = create_food_log(food_data)

        return jsonify({
            "success": True,
            "message": "Food added successfully",
            "foodId": str(result.inserted_id)
        }), 201

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500