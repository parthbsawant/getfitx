from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config.db import db

users_collection = db["users"]

@jwt_required()
def set_goal():

    try:

        # Current logged in user
        current_user_email = get_jwt_identity()

        # Frontend data
        data = request.get_json()

        age = data.get("age")
        weight = data.get("weight")
        height = data.get("height")
        goal_weight = data.get("goalWeight")
        deadline_days = data.get("deadlineDays")
        gender = data.get("gender")

        # STEP 1 — Calculate BMR

        if gender.lower() == "male":

            bmr = (
                (10 * weight)
                + (6.25 * height)
                - (5 * age)
                + 5
            )

        else:

            bmr = (
                (10 * weight)
                + (6.25 * height)
                - (5 * age)
                - 161
            )

        # STEP 2 — Maintenance Calories

        maintenance_calories = bmr * 1.2

        # STEP 3 — Required Deficit

        weight_difference = weight - goal_weight

        required_deficit = (
            (weight_difference * 7700)
            / deadline_days
        )

        # STEP 4 — Target Calories

        target_calories = (
            maintenance_calories
            - required_deficit
        )

        # STEP 5 — Save Goal Data

        users_collection.update_one(
            {
                "email": current_user_email
            },
            {
                "$set": {
                    "age": age,
                    "weight": weight,
                    "height": height,
                    "goalWeight": goal_weight,
                    "deadlineDays": deadline_days,
                    "gender": gender,
                    "bmr": round(bmr, 2),
                    "maintenanceCalories": round(maintenance_calories, 2),
                    "requiredDeficit": round(required_deficit, 2),
                    "targetCalories": round(target_calories, 2)
                }
            }
        )

        return jsonify({
            "message": "Goal set successfully",

            "goalData": {
                "bmr": round(bmr, 2),
                "maintenanceCalories": round(maintenance_calories, 2),
                "requiredDeficit": round(required_deficit, 2),
                "targetCalories": round(target_calories, 2)
            }
        }), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500