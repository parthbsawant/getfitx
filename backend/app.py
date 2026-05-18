from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from config.db import db
from routes.auth_routes import auth_bp
from routes.goal_routes import goal_bp
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# JWT Configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

# Initialize JWT
jwt = JWTManager(app)

# Register Blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(goal_bp)

@app.route('/')
@app.route('/')
def home():
    return {
        "message": "GetFitX Backend Running Successfully"
    }

if __name__ == '__main__':
    app.run(debug=True)