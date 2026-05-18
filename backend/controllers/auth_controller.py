from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from flask import request, jsonify
from config.db import db
import bcrypt

# Users Collection
users_collection = db["users"]

def login():

    try:

        # Get frontend data
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        # Find user
        user = users_collection.find_one({
            "email": email
        })

        # Check if user exists
        if not user:
            return jsonify({
                "error": "User not found"
            }), 404

        # Verify password
        password_match = bcrypt.checkpw(
            password.encode('utf-8'),
            user["password"].encode('utf-8')
        )

        if not password_match:
            return jsonify({
                "error": "Invalid password"
            }), 401

        # Generate JWT token
        access_token = create_access_token(
            identity=email
        )

        return jsonify({
            "message": "Login successful",
            "token": access_token
        }), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

def signup():

    try:
        # Get data from frontend
        data = request.get_json()

        print("Incoming Data:", data)

        # Extract user details
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        # Check existing user
        existing_user = users_collection.find_one({
            "email": email
        })

        if existing_user:
            return jsonify({
                "error": "User already exists"
            }), 400

        # Hash password
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        print("Hashed Password:", hashed_password)

        # Create user object
        new_user = {
            "name": name,
            "email": email,
            "password": hashed_password
        }

        print("User Object:", new_user)

        # Insert into MongoDB
        result = users_collection.insert_one(new_user)

        print("Inserted ID:", result.inserted_id)

        return jsonify({
            "message": "User registered successfully"
        }), 201

    except Exception as e:

        print("ERROR:", str(e))

        return jsonify({
            "error": str(e)
        }), 500
    

@jwt_required()
def get_profile():

    try:

        # Get current logged in user email
        current_user_email = get_jwt_identity()

        # Find user in DB
        user = users_collection.find_one({
            "email": current_user_email
        })

        if not user:
            return jsonify({
                "error": "User not found"
            }), 404

        # Convert ObjectId to string
        user["_id"] = str(user["_id"])

        # Remove password before sending response
        user.pop("password", None)

        return jsonify({
            "message": "Profile fetched successfully",
            "user": user
        }), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500
    