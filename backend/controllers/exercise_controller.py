from flask import request, jsonify
from datetime import datetime
import pytz
from models.exercise_model import (
    create_exercise_log,
    get_exercises_by_user_and_date,
    get_exercises_by_user,
    delete_exercise_log
)

IST = pytz.timezone("Asia/Kolkata")

def add_exercise():
    try:
        data = request.get_json()
        user_id = data.get("userId")
        exercise_name = data.get("exerciseName")
        duration = data.get("duration") # in minutes
        calories_burned = data.get("caloriesBurned") # in kcal

        if not user_id or not exercise_name or duration is None or calories_burned is None:
            return jsonify({
                "success": False,
                "message": "userId, exerciseName, duration, and caloriesBurned are required"
            }), 400

        exercise_data = {
            "userId": user_id,
            "exerciseName": exercise_name,
            "duration": int(duration),
            "caloriesBurned": float(calories_burned),
            "loggedAt": datetime.now(IST)
        }

        result = create_exercise_log(exercise_data)

        return jsonify({
            "success": True,
            "message": "Exercise logged successfully",
            "exerciseLogId": str(result.inserted_id)
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

def get_today_exercise(user_id):
    try:
        now_ist = datetime.now(IST)
        start_date = now_ist.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now_ist.replace(hour=23, minute=59, second=59, microsecond=999999)

        logs = get_exercises_by_user_and_date(user_id, start_date, end_date)
        total_calories_burned = sum(log.get("caloriesBurned", 0) for log in logs)
        total_duration = sum(log.get("duration", 0) for log in logs)

        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                "id": str(log["_id"]),
                "exerciseName": log.get("exerciseName"),
                "duration": log.get("duration"),
                "caloriesBurned": log.get("caloriesBurned"),
                "loggedAt": log.get("loggedAt").astimezone(IST).strftime("%I:%M %p")
            })

        return jsonify({
            "success": True,
            "totalCaloriesBurned": round(total_calories_burned, 2),
            "totalDuration": total_duration,
            "logs": formatted_logs
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

def get_exercise_history(user_id):
    try:
        logs = get_exercises_by_user(user_id)
        
        # Group by date YYYY-MM-DD
        exercise_by_date = {}
        for log in logs:
            logged_at = log.get("loggedAt")
            if not logged_at:
                continue
            date_str = logged_at.astimezone(IST).strftime("%Y-%m-%d")
            
            if date_str not in exercise_by_date:
                exercise_by_date[date_str] = {
                    "totalCaloriesBurned": 0,
                    "totalDuration": 0,
                    "workouts": []
                }
            
            exercise_by_date[date_str]["totalCaloriesBurned"] += log.get("caloriesBurned", 0)
            exercise_by_date[date_str]["totalDuration"] += log.get("duration", 0)
            exercise_by_date[date_str]["workouts"].append({
                "id": str(log["_id"]),
                "exerciseName": log.get("exerciseName"),
                "duration": log.get("duration"),
                "caloriesBurned": log.get("caloriesBurned"),
                "loggedAt": logged_at.astimezone(IST).strftime("%I:%M %p")
            })

        history = []
        for date, info in exercise_by_date.items():
            history.append({
                "date": date,
                "totalCaloriesBurned": round(info["totalCaloriesBurned"], 2),
                "totalDuration": info["totalDuration"],
                "workouts": info["workouts"]
            })
        
        # Sort by date descending (most recent first)
        history.sort(key=lambda x: x["date"], reverse=True)

        return jsonify({
            "success": True,
            "exerciseHistory": history
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

def delete_exercise(log_id):
    try:
        result = delete_exercise_log(log_id)
        if result.deleted_count == 0:
            return jsonify({
                "success": False,
                "message": "Exercise log not found"
            }), 404

        return jsonify({
            "success": True,
            "message": "Exercise log deleted successfully"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
