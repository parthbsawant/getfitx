from config.db import db
from bson import ObjectId

water_collection = db["water_logs"]

def create_water_log(data):
    return water_collection.insert_one(data)

def get_water_by_user_and_date(user_id, start_date, end_date):
    return list(
        water_collection.find({
            "userId": user_id,
            "loggedAt": {
                "$gte": start_date,
                "$lte": end_date
            }
        })
    )

def get_water_by_user(user_id):
    return list(
        water_collection.find({
            "userId": user_id
        }).sort("loggedAt", 1)
    )

def delete_water_log(log_id):
    return water_collection.delete_one({
        "_id": ObjectId(log_id)
    })
