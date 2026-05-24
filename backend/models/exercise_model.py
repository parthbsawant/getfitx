from config.db import db
from bson import ObjectId

exercise_collection = db["exercise_logs"]

def create_exercise_log(data):
    return exercise_collection.insert_one(data)

def get_exercises_by_user_and_date(user_id, start_date, end_date):
    return list(
        exercise_collection.find({
            "userId": user_id,
            "loggedAt": {
                "$gte": start_date,
                "$lte": end_date
            }
        })
    )

def get_exercises_by_user(user_id):
    return list(
        exercise_collection.find({
            "userId": user_id
        }).sort("loggedAt", 1)
    )

def delete_exercise_log(log_id):
    return exercise_collection.delete_one({
        "_id": ObjectId(log_id)
    })
