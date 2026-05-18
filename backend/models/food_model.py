from config.db import db
from datetime import datetime


food_collection = db["food_logs"]


def create_food_log(data):
    return food_collection.insert_one(data)


def get_foods_by_user_and_date(user_id, start_date, end_date):
    return list(
        food_collection.find({
            "userId": user_id,
            "consumedAt": {
                "$gte": start_date,
                "$lte": end_date
            }
        })
    )


def delete_food_log(food_id):
    from bson import ObjectId

    return food_collection.delete_one({
        "_id": ObjectId(food_id)
    })

def get_foods_by_user(user_id):

    return list(
        food_collection.find({
            "userId": user_id
        })
    )