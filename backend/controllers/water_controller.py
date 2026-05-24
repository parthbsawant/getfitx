from flask import request, jsonify
from datetime import datetime, timedelta
import pytz
from models.water_model import (
    create_water_log,
    get_water_by_user_and_date,
    get_water_by_user,
    delete_water_log
)
from config.db import db

IST = pytz.timezone("Asia/Kolkata")
users_collection = db["users"]

def add_water():
    try:
        data = request.get_json()
        user_id = data.get("userId")
        amount = data.get("amount") # in ml

        if not user_id or not amount:
            return jsonify({
                "success": False,
                "message": "userId and amount are required"
            }), 400

        water_data = {
            "userId": user_id,
            "amount": int(amount),
            "loggedAt": datetime.now(IST)
        }

        result = create_water_log(water_data)

        return jsonify({
            "success": True,
            "message": "Water logged successfully",
            "waterLogId": str(result.inserted_id)
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

def get_today_water(user_id):
    try:
        now_ist = datetime.now(IST)
        start_date = now_ist.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now_ist.replace(hour=23, minute=59, second=59, microsecond=999999)

        logs = get_water_by_user_and_date(user_id, start_date, end_date)
        total_water = sum(log.get("amount", 0) for log in logs)

        # Get water goal from user profile
        user = users_collection.find_one({"email": user_id})
        water_goal = 2000
        if user and "waterGoal" in user:
            water_goal = user["waterGoal"]

        progress_percentage = round((total_water / water_goal) * 100, 2) if water_goal > 0 else 0

        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                "id": str(log["_id"]),
                "amount": log.get("amount"),
                "loggedAt": log.get("loggedAt").astimezone(IST).strftime("%I:%M %p")
            })

        return jsonify({
            "success": True,
            "totalWater": total_water,
            "waterGoal": water_goal,
            "progressPercentage": progress_percentage,
            "logs": formatted_logs
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

def get_water_history(user_id):
    try:
        logs = get_water_by_user(user_id)
        
        # Group by date YYYY-MM-DD
        water_by_date = {}
        for log in logs:
            logged_at = log.get("loggedAt")
            if not logged_at:
                continue
            date_str = logged_at.astimezone(IST).strftime("%Y-%m-%d")
            water_by_date[date_str] = water_by_date.get(date_str, 0) + log.get("amount", 0)

        history = []
        for date, amount in water_by_date.items():
            history.append({
                "date": date,
                "amount": amount
            })
        
        # Sort by date descending (most recent first)
        history.sort(key=lambda x: x["date"], reverse=True)

        return jsonify({
            "success": True,
            "waterHistory": history
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

def delete_water(log_id):
    try:
        result = delete_water_log(log_id)
        if result.deleted_count == 0:
            return jsonify({
                "success": False,
                "message": "Water log not found"
            }), 404

        return jsonify({
            "success": True,
            "message": "Water log deleted successfully"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

def set_water_goal():
    try:
        data = request.get_json()
        user_id = data.get("userId")
        water_goal = data.get("waterGoal") # in ml

        if not user_id or not water_goal:
            return jsonify({
                "success": False,
                "message": "userId and waterGoal are required"
            }), 400

        result = users_collection.update_one(
            {"email": user_id},
            {"$set": {"waterGoal": int(water_goal)}}
        )

        if result.matched_count == 0:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        return jsonify({
            "success": True,
            "message": "Water goal updated successfully",
            "waterGoal": int(water_goal)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
