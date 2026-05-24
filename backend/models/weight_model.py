from config.db import db

weight_collection = db["weight_logs"]


def create_weight_log(data):

    return weight_collection.insert_one(data)


def get_weights_by_user(user_id):

    return list(
        weight_collection.find(
            {
                "userId": user_id
            }
        ).sort("loggedAt", 1)
    )

def get_latest_weight(user_id):

    return weight_collection.find_one(

        {
            "userId": user_id
        },

        sort=[("loggedAt", -1)]
    )
