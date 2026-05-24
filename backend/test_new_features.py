import unittest
import json
from datetime import datetime, timedelta
import pytz
from app import app
from config.db import db

IST = pytz.timezone("Asia/Kolkata")
TEST_USER = "test_verify_user@example.com"

class TestGetFitXBackendUpgrades(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        
        # Clean up any potential lingering test data first
        cls.cleanup_db()
        
        # Insert mock user
        db.users.insert_one({
            "name": "Verification User",
            "email": TEST_USER,
            "maintenanceCalories": 2200.0,
            "targetCalories": 1700.0,
            "goalWeight": 70.0,
            "weight": 80.0,
            "streakFreezesAvailable": 2,
            "frozenDates": [],
            "waterGoal": 2000,
            "proteinGoal": 120,
            "carbGoal": 180,
            "fatGoal": 60
        })
        
        now_ist = datetime.now(IST)
        
        # Insert mock food logs
        # Today: 1500 kcal total
        db.food_logs.insert_many([
            {"userId": TEST_USER, "foodName": "Oats", "calories": 400.0, "protein": 15.0, "carbs": 60.0, "fats": 8.0, "mealType": "breakfast", "consumedAt": now_ist},
            {"userId": TEST_USER, "foodName": "Chicken Rice", "calories": 600.0, "protein": 40.0, "carbs": 70.0, "fats": 12.0, "mealType": "lunch", "consumedAt": now_ist},
            {"userId": TEST_USER, "foodName": "Protein Shake", "calories": 500.0, "protein": 30.0, "carbs": 10.0, "fats": 5.0, "mealType": "snacks", "consumedAt": now_ist}
        ])
        
        # Yesterday: 1800 kcal total
        yesterday_ist = now_ist - timedelta(days=1)
        db.food_logs.insert_many([
            {"userId": TEST_USER, "foodName": "Eggs", "calories": 300.0, "protein": 18.0, "carbs": 2.0, "fats": 20.0, "mealType": "breakfast", "consumedAt": yesterday_ist},
            {"userId": TEST_USER, "foodName": "Fish and Salad", "calories": 700.0, "protein": 45.0, "carbs": 20.0, "fats": 15.0, "mealType": "lunch", "consumedAt": yesterday_ist},
            {"userId": TEST_USER, "foodName": "Pasta", "calories": 800.0, "protein": 20.0, "carbs": 120.0, "fats": 25.0, "mealType": "dinner", "consumedAt": yesterday_ist}
        ])
        
        # Insert mock exercise logs
        # Today: 300 kcal burned
        db.exercise_logs.insert_one({
            "userId": TEST_USER,
            "exerciseName": "Running",
            "duration": 30,
            "caloriesBurned": 300.0,
            "loggedAt": now_ist
        })
        # Yesterday: 400 kcal burned
        db.exercise_logs.insert_one({
            "userId": TEST_USER,
            "exerciseName": "Cycling",
            "duration": 45,
            "caloriesBurned": 400.0,
            "loggedAt": yesterday_ist
        })

        # Insert mock water logs
        # Today: 750 ml
        db.water_logs.insert_many([
            {"userId": TEST_USER, "amount": 500, "loggedAt": now_ist},
            {"userId": TEST_USER, "amount": 250, "loggedAt": now_ist}
        ])

        # Insert mock weight logs
        db.weight_logs.insert_many([
            {"userId": TEST_USER, "weight": 79.5, "loggedAt": now_ist - timedelta(days=3)},
            {"userId": TEST_USER, "weight": 78.5, "loggedAt": now_ist}
        ])

    @classmethod
    def tearDownClass(cls):
        cls.cleanup_db()

    @classmethod
    def cleanup_db(cls):
        db.users.delete_many({"email": TEST_USER})
        db.food_logs.delete_many({"userId": TEST_USER})
        db.exercise_logs.delete_many({"userId": TEST_USER})
        db.water_logs.delete_many({"userId": TEST_USER})
        db.weight_logs.delete_many({"userId": TEST_USER})

    def test_01_dashboard_with_exercise(self):
        """Test that food dashboard reflects today's exercise calories"""
        response = self.client.get(f"/api/food/dashboard/{TEST_USER}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        dashboard = data["dashboardData"]
        self.assertEqual(dashboard["consumedCalories"], 1500.0)
        self.assertEqual(dashboard["caloriesBurned"], 300.0)
        self.assertEqual(dashboard["netCalories"], 1200.0) # 1500 - 300
        self.assertEqual(dashboard["remainingCalories"], 500.0) # 1700 - 1200

    def test_02_water_endpoints(self):
        """Test water tracking endpoints (today, history, goal)"""
        # Test today's water
        response = self.client.get(f"/api/water/today/{TEST_USER}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["totalWater"], 750)
        self.assertEqual(data["waterGoal"], 2000)
        self.assertEqual(data["progressPercentage"], 37.5) # 750/2000 * 100
        self.assertEqual(len(data["logs"]), 2)

        # Test water goal update
        response = self.client.post("/api/water/goal", json={
            "userId": TEST_USER,
            "waterGoal": 3000
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["waterGoal"], 3000)

        # Test water history
        response = self.client.get(f"/api/water/history/{TEST_USER}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["waterHistory"][0]["amount"], 750)

    def test_03_exercise_endpoints(self):
        """Test exercise logging endpoints (today, history)"""
        response = self.client.get(f"/api/exercise/today/{TEST_USER}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["totalCaloriesBurned"], 300.0)
        self.assertEqual(data["totalDuration"], 30)
        self.assertEqual(len(data["logs"]), 1)

        response = self.client.get(f"/api/exercise/history/{TEST_USER}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["exerciseHistory"]), 2)

    def test_04_calorie_analytics(self):
        """Test monthly calorie analytics"""
        response = self.client.get(f"/api/analytics/calories/{TEST_USER}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["averageIntake"], round(3300.0 / 30.0, 2)) # 1500 (today) + 1800 (yesterday)
        self.assertEqual(data["highestCalorieDay"]["calories"], 1800.0)

    def test_05_fat_loss_estimation(self):
        """Test fat loss estimation calculation"""
        response = self.client.get(f"/api/analytics/fat-loss/{TEST_USER}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        
        fat_loss = data["fatLossEstimation"]
        # Deficits:
        # Today: net consumed = 1200 (1500-300). Deficit = 2200 - 1200 = 1000
        # Yesterday: net consumed = 1400 (1800-400). Deficit = 2200 - 1400 = 800
        # Cumulative Deficit = 1800
        # Estimated fat lost = 1800 / 7700 = 0.23 kg
        self.assertEqual(fat_loss["cumulativeDeficit"], 1800.0)
        self.assertEqual(fat_loss["estimatedFatLostKg"], 0.23)
        self.assertEqual(fat_loss["weeklyFatLossKg"], 0.23)
        self.assertEqual(fat_loss["monthlyFatLossKg"], 0.23)
        # Weight diff: 79.5 (starting weight from logs) - 70 (goal) = 9.5 kg target loss
        # Progress: 0.23 / 9.5 * 100 = 2.42%
        self.assertEqual(fat_loss["progressPercentage"], 2.42)

    def test_06_meal_distribution(self):
        """Test meal distribution calculations"""
        response = self.client.get(f"/api/analytics/meal-distribution/{TEST_USER}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        
        dist = data["mealDistribution"]
        # Calories breakdown (last 30 days):
        # Breakfast: Oats (400) + Eggs (300) = 700 kcal (21.21%)
        # Lunch: Chicken Rice (600) + Fish (700) = 1300 kcal (39.39%)
        # Dinner: Pasta (800) = 800 kcal (24.24%)
        # Snacks: Protein Shake (500) = 500 kcal (15.15%)
        # Total = 3300 kcal
        self.assertEqual(dist["breakfast"], 21.21)
        self.assertEqual(dist["lunch"], 39.39)
        self.assertEqual(dist["dinner"], 24.24)
        self.assertEqual(dist["snacks"], 15.15)

    def test_07_macro_analytics(self):
        """Test macro analytics and protein deficiency alerts"""
        response = self.client.get(f"/api/analytics/macros/{TEST_USER}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        
        macros = data["macros"]
        # Today: 15+40+30 = 85g protein, 60+70+10 = 140g carbs, 8+12+5 = 25g fats.
        self.assertEqual(macros["todayMacros"]["protein"], 85.0)
        self.assertEqual(macros["todayMacros"]["carbs"], 140.0)
        self.assertEqual(macros["todayMacros"]["fats"], 25.0)
        self.assertEqual(macros["progressPercentage"]["protein"], round(85.0 / 120.0 * 100, 2))

    def test_08_smart_insights(self):
        """Test smart coaching insights list generation"""
        response = self.client.get(f"/api/analytics/insights/{TEST_USER}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertGreater(len(data["insights"]), 0)
        # Check structure
        self.assertIn("category", data["insights"][0])
        self.assertIn("title", data["insights"][0])
        self.assertIn("message", data["insights"][0])

    def test_09_advanced_streaks(self):
        """Test advanced streaks calculations and streak freeze"""
        response = self.client.get(f"/api/streak/advanced/{TEST_USER}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        
        streak = data["streakData"]
        self.assertEqual(streak["foodStreak"]["currentStreak"], 2) # Today & yesterday logged
        self.assertEqual(streak["streakFreezeInfo"]["availableFreezes"], 2)

        # Apply streak freeze for 2 days ago
        two_days_ago = (datetime.now(IST) - timedelta(days=2)).strftime("%Y-%m-%d")
        response = self.client.post("/api/streak/freeze", json={
            "userId": TEST_USER,
            "date": two_days_ago
        })
        self.assertEqual(response.status_code, 200)
        
        # Re-check streak (should include frozen date, lengthening streak to 3 days!)
        response = self.client.get(f"/api/streak/advanced/{TEST_USER}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        streak = data["streakData"]
        self.assertEqual(streak["foodStreak"]["currentStreak"], 3) # Today, yesterday, and 2 days ago (frozen)
        self.assertEqual(streak["streakFreezeInfo"]["availableFreezes"], 1)

if __name__ == "__main__":
    unittest.main()
