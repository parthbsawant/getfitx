from flask import request, jsonify
from datetime import datetime
from models.food_model import (
    create_food_log,
    get_foods_by_user_and_date,
    delete_food_log,
    get_foods_by_user
)
from models.food_model import (
    get_all_food_dates
)
from config.db import db
import pytz

IST = pytz.timezone("Asia/Kolkata")
users_collection = db["users"]

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
            "consumedAt": datetime.now(IST)
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
    
def get_today_foods(user_id):

    try:

        # START OF TODAY
        start_date = datetime.utcnow().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        # END OF TODAY
        end_date = datetime.utcnow().replace(
            hour=23,
            minute=59,
            second=59,
            microsecond=999999
        )

        foods = get_foods_by_user_and_date(
            user_id,
            start_date,
            end_date
        )

        total_calories = 0

        formatted_foods = []

        for food in foods:

            total_calories += food.get("calories", 0)

            formatted_foods.append({
                "id": str(food["_id"]),
                "foodName": food.get("foodName"),
                "calories": food.get("calories"),
                "protein": food.get("protein"),
                "carbs": food.get("carbs"),
                "fats": food.get("fats"),
                "quantity": food.get("quantity"),
                "mealType": food.get("mealType"),
                "consumedAt": food.get("consumedAt")
            })

        return jsonify({
            "success": True,
            "totalCalories": total_calories,
            "foods": formatted_foods
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
    
def delete_food(food_id):

    try:

        result = delete_food_log(food_id)

        if result.deleted_count == 0:

            return jsonify({
                "success": False,
                "message": "Food not found"
            }), 404

        return jsonify({
            "success": True,
            "message": "Food deleted successfully"
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
    
def get_dashboard_data(user_id):

    try:

        # TODAY DATE RANGE
        start_date = datetime.utcnow().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        end_date = datetime.utcnow().replace(
            hour=23,
            minute=59,
            second=59,
            microsecond=999999
        )

        # GET TODAY'S FOODS
        foods = get_foods_by_user_and_date(
            user_id,
            start_date,
            end_date
        )

        # TOTAL CONSUMED
        consumed_calories = sum(
            food.get("calories", 0)
            for food in foods
        )

        # GET TODAY'S EXERCISE BURNED CALORIES
        from models.exercise_model import get_exercises_by_user_and_date as get_exercises
        exercises = get_exercises(
            user_id,
            start_date,
            end_date
        )
        calories_burned = sum(
            ex.get("caloriesBurned", 0)
            for ex in exercises
        )

        # FIND USER
        user = users_collection.find_one({
            "email": user_id
        })

        if not user:

            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        # USER GOAL DATA
        target_calories = user.get("targetCalories", 0)

        maintenance_calories = user.get(
            "maintenanceCalories",
            0
        )

        required_deficit = user.get(
            "requiredDeficit",
            0
        )

        # NET CONSUMED CALORIES
        net_calories = consumed_calories - calories_burned

        # REMAINING CALORIES
        remaining_calories = (
            target_calories
            - net_calories
        )

        # SURPLUS CHECK
        surplus = 0

        if remaining_calories < 0:
            surplus = abs(remaining_calories)

        return jsonify({

            "success": True,

            "dashboardData": {

                "maintenanceCalories":
                    round(maintenance_calories, 2),

                "targetCalories":
                    round(target_calories, 2),

                "consumedCalories":
                    round(consumed_calories, 2),

                "caloriesBurned":
                    round(calories_burned, 2),

                "netCalories":
                    round(net_calories, 2),

                "remainingCalories":
                    round(remaining_calories, 2),

                "requiredDeficit":
                    round(required_deficit, 2),

                "surplus":
                    round(surplus, 2)
            }

        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
    
def get_weekly_analytics(user_id):

    try:

        # GET ALL USER FOODS
        foods = get_foods_by_user(user_id)

        # STORE DATEWISE TOTALS
        calories_by_date = {}

        for food in foods:

            consumed_at = food.get("consumedAt")

            if not consumed_at:
                continue

            # FORMAT DATE
            date_str = consumed_at.strftime("%Y-%m-%d")

            # CREATE KEY IF NOT EXISTS
            if date_str not in calories_by_date:

                calories_by_date[date_str] = 0

            # ADD CALORIES
            calories_by_date[date_str] += food.get(
                "calories",
                0
            )

        # CONVERT TO ARRAY
        analytics_data = []

        for date, calories in calories_by_date.items():

            analytics_data.append({

                "date": date,
                "calories": round(calories, 2)

            })

        # SORT BY DATE
        analytics_data.sort(
            key=lambda x: x["date"]
        )

        return jsonify({

            "success": True,
            "weeklyAnalytics": analytics_data

        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
    
def get_streak_data(user_id):

    try:

        foods = get_all_food_dates(user_id)

        if not foods:

            return jsonify({
                "success": True,
                "currentStreak": 0,
                "longestStreak": 0
            }), 200

        # UNIQUE DATES
        unique_dates = set()

        for food in foods:

            consumed_date = food.get(
                "consumedAt"
            )

            if consumed_date:

                unique_dates.add(
                    consumed_date.date()
                )

        sorted_dates = sorted(unique_dates)

        current_streak = 1
        longest_streak = 1

        for i in range(1, len(sorted_dates)):

            difference = (
                sorted_dates[i]
                - sorted_dates[i - 1]
            ).days

            if difference == 1:

                current_streak += 1

                longest_streak = max(
                    longest_streak,
                    current_streak
                )

            elif difference > 1:

                current_streak = 1

        # CHECK IF TODAY IS INCLUDED
        from datetime import datetime

        from datetime import datetime

        today = datetime.utcnow().date()

        last_logged_date = sorted_dates[-1]

        difference = (
            today - last_logged_date
        ).days

        # ALLOW TODAY OR YESTERDAY
        if difference > 1:

            current_streak = 0

        return jsonify({
            "success": True,
            "currentStreak": current_streak,
            "longestStreak": longest_streak
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500