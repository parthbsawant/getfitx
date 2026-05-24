from flask import request, jsonify
from datetime import datetime, timedelta
import pytz
from services.streak_service import (
    get_advanced_streak_data,
    apply_streak_freeze,
    add_streak_freezes
)

IST = pytz.timezone("Asia/Kolkata")

def get_advanced_streak(user_id):
    try:
        data = get_advanced_streak_data(user_id)
        if data is None:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404
            
        return jsonify({
            "success": True,
            "streakData": data
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

def freeze_streak():
    try:
        data = request.get_json()
        user_id = data.get("userId")
        # Optional date to freeze, default to yesterday
        date_str = data.get("date")
        
        if not user_id:
            return jsonify({
                "success": False,
                "message": "userId is required"
            }), 400
            
        if not date_str:
            yesterday = datetime.now(IST) - timedelta(days=1)
            date_str = yesterday.strftime("%Y-%m-%d")
            
        success, message = apply_streak_freeze(user_id, date_str)
        if not success:
            return jsonify({
                "success": False,
                "message": message
            }), 400
            
        return jsonify({
            "success": True,
            "message": message,
            "frozenDate": date_str
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

def grant_freezes():
    try:
        data = request.get_json()
        user_id = data.get("userId")
        count = data.get("count", 1)
        
        if not user_id:
            return jsonify({
                "success": False,
                "message": "userId is required"
            }), 400
            
        success, message = add_streak_freezes(user_id, int(count))
        if not success:
            return jsonify({
                "success": False,
                "message": message
            }), 400
            
        return jsonify({
            "success": True,
            "message": message
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
