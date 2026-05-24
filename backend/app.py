from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from config.db import db
from routes.auth_routes import auth_bp
from routes.goal_routes import goal_bp
from routes.food_routes import food_bp
from routes.nutrition_routes import nutrition_bp
from routes.gemini_routes import gemini_bp
from routes.weight_routes import weight_bp
from routes.analytics_routes import analytics_bp
from routes.streak_routes import streak_bp
from routes.water_routes import water_bp
from routes.exercise_routes import exercise_bp
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
app.register_blueprint(food_bp, url_prefix="/api/food")
app.register_blueprint(nutrition_bp,url_prefix="/api/nutrition")
app.register_blueprint(gemini_bp,url_prefix="/api/ai")
app.register_blueprint(weight_bp,url_prefix="/api/weight")
app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
app.register_blueprint(streak_bp, url_prefix="/api/streak")
app.register_blueprint(water_bp, url_prefix="/api/water")
app.register_blueprint(exercise_bp, url_prefix="/api/exercise")

@app.route('/')
@app.route('/')
def home():
    return {
        "message": "GetFitX Backend Running Successfully"
    }

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)