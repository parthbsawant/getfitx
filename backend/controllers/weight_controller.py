from flask import request, jsonify
from datetime import datetime
from datetime import timedelta

from models.weight_model import (
    create_weight_log,
    get_weights_by_user,
    get_latest_weight
)
import pytz
IST = pytz.timezone("Asia/Kolkata")

def add_weight():

    try:

        data = request.get_json()

        weight_data = {

            "userId": data.get("userId"),
            "weight": data.get("weight"),
            "loggedAt": datetime.now()
        }

        result = create_weight_log(weight_data)

        return jsonify({

            "success": True,
            "message": "Weight logged successfully",
            "weightLogId": str(result.inserted_id)

        }), 201

    except Exception as e:

        return jsonify({

            "success": False,
            "message": str(e)

        }), 500


def get_weight_history(user_id):

    try:

        weights = get_weights_by_user(user_id)

        formatted_weights = []

        for item in weights:

            formatted_weights.append({

            "id": str(item["_id"]),
            "weight": item.get("weight"),

            "loggedAt":
                item.get("loggedAt")
                .astimezone(IST)
                .strftime("%d-%m-%Y %I:%M %p")
        })

        return jsonify({

            "success": True,
            "weightHistory": formatted_weights

        }), 200

    except Exception as e:

        return jsonify({

            "success": False,
            "message": str(e)

        }), 500
    
def get_weight_analytics(user_id):

    try:

        weights = get_weights_by_user(user_id)
        print(weights)

        if len(weights) == 0:

            return jsonify({

                "success": False,
                "message": "No weight data found"

            }), 404

        # SORT BY DATE

        weights.sort(
            key=lambda x: x["loggedAt"]
        )

        # STARTING WEIGHT
        starting_weight = weights[0]["weight"]

        # CURRENT WEIGHT
        current_weight = weights[-1]["weight"]

        # TOTAL LOSS
        total_weight_lost = (
            starting_weight - current_weight
        )

        # WEEKLY CHANGE

        weekly_change = 0

        one_week_ago = datetime.now() - timedelta(days=7)

        weekly_weights = [

            w for w in weights
            if w["loggedAt"] >= one_week_ago
        ]

        if len(weekly_weights) >= 2:

            weekly_change = (

                weekly_weights[0]["weight"]
                -
                weekly_weights[-1]["weight"]
            )

        # MONTHLY CHANGE

        monthly_change = 0

        one_month_ago = datetime.now() - timedelta(days=30)

        monthly_weights = [

            w for w in weights
            if w["loggedAt"] >= one_month_ago
        ]

        if len(monthly_weights) >= 2:

            monthly_change = (

                monthly_weights[0]["weight"]
                -
                monthly_weights[-1]["weight"]
            )

        # GOAL WEIGHT

        from config.db import db

        users_collection = db["users"]

        user = users_collection.find_one({

            "email": user_id
        })

        goal_weight = user.get("goalWeight", 0)

        # PROGRESS %

        progress_percentage = 0

        if goal_weight:

            total_target_loss = (

                starting_weight
                -
                goal_weight
            )

            achieved_loss = (

                starting_weight
                -
                current_weight
            )

            if total_target_loss > 0:

                progress_percentage = (

                    achieved_loss
                    /
                    total_target_loss
                ) * 100

        return jsonify({

            "success": True,

            "analytics": {

                "startingWeight":
                    round(starting_weight, 2),

                "currentWeight":
                    round(current_weight, 2),

                "totalWeightLost":
                    round(total_weight_lost, 2),

                "weeklyChange":
                    round(weekly_change, 2),

                "monthlyChange":
                    round(monthly_change, 2),

                "goalWeight":
                    goal_weight,

                "progressPercentage":
                    round(progress_percentage, 2)
            }

        }), 200

    except Exception as e:

        return jsonify({

            "success": False,
            "message": str(e)

        }), 500