from datetime import datetime, timedelta
import pytz
from config.db import db
from models.food_model import get_foods_by_user
from models.exercise_model import get_exercises_by_user
from models.water_model import get_water_by_user

IST = pytz.timezone("Asia/Kolkata")
users_collection = db["users"]

def generate_coaching_insights(user_id):
    user = users_collection.find_one({"email": user_id})
    if not user:
        return []
        
    target_calories = user.get("targetCalories", 2000.0)
    maintenance_calories = user.get("maintenanceCalories", 2000.0)
    water_goal = user.get("waterGoal", 2000)
    protein_goal = user.get("proteinGoal") if user.get("proteinGoal") else int((target_calories * 0.30) / 4)

    now_ist = datetime.now(IST)
    today = now_ist.date()

    # Retrieve all logs
    foods = get_foods_by_user(user_id)
    exercises = get_exercises_by_user(user_id)
    waters = get_water_by_user(user_id)

    # Group foods, exercises, waters by local date
    daily_food = {}
    daily_protein = {}
    for food in foods:
        consumed_at = food.get("consumedAt")
        if not consumed_at:
            continue
        d = consumed_at.astimezone(IST).date()
        daily_food[d] = daily_food.get(d, 0.0) + food.get("calories", 0.0)
        daily_protein[d] = daily_protein.get(d, 0.0) + food.get("protein", 0.0)

    daily_exercise = {}
    for ex in exercises:
        logged_at = ex.get("loggedAt")
        if not logged_at:
            continue
        d = logged_at.astimezone(IST).date()
        daily_exercise[d] = daily_exercise.get(d, 0.0) + ex.get("caloriesBurned", 0.0)

    daily_water = {}
    for w in waters:
        logged_at = w.get("loggedAt")
        if not logged_at:
            continue
        d = logged_at.astimezone(IST).date()
        daily_water[d] = daily_water.get(d, 0.0) + w.get("amount", 0)

    insights = []

    # 1. Calorie Target Adherence (last 7 days)
    exceeded_count = 0
    active_days_7 = 0
    for i in range(7):
        d = today - timedelta(days=i)
        calories = daily_food.get(d, 0.0)
        if calories > 0:
            active_days_7 += 1
            if calories > target_calories:
                exceeded_count += 1

    if active_days_7 > 0:
        if exceeded_count == 0:
            insights.append({
                "category": "Nutrition",
                "title": "Calorie Champion",
                "message": "Perfect discipline! You stayed within your daily calorie target every single day you logged this week.",
                "type": "success"
            })
        else:
            insights.append({
                "category": "Nutrition",
                "title": "Calorie Adherence",
                "message": f"You exceeded your daily calorie target {exceeded_count} time(s) in the last 7 days. Consistency is key, try logging meals before eating!",
                "type": "warning"
            })

    # 2. Deficit Insight (last 30 days)
    total_deficit = 0.0
    logged_days_30 = 0
    for i in range(30):
        d = today - timedelta(days=i)
        if d in daily_food or d in daily_exercise:
            logged_days_30 += 1
            food_cal = daily_food.get(d, 0.0)
            ex_cal = daily_exercise.get(d, 0.0)
            net_cal = food_cal - ex_cal
            total_deficit += (maintenance_calories - net_cal)

    if logged_days_30 > 0:
        avg_deficit = round(total_deficit / 30.0, 1)
        if avg_deficit > 0:
            insights.append({
                "category": "Weight Loss",
                "title": "Monthly Deficit",
                "message": f"Your average deficit this month is {avg_deficit} kcal/day. You are on track for steady fat loss!",
                "type": "success"
            })
        else:
            insights.append({
                "category": "Weight Loss",
                "title": "Calorie Balance",
                "message": f"Your average daily intake is {abs(avg_deficit)} kcal above maintenance this month. Consider creating a larger deficit to promote fat loss.",
                "type": "info"
            })

    # 3. Consistency Improvement
    current_week_count = 0
    for i in range(7):
        d = today - timedelta(days=i)
        if d in daily_food:
            current_week_count += 1
            
    previous_week_count = 0
    for i in range(7, 14):
        d = today - timedelta(days=i)
        if d in daily_food:
            previous_week_count += 1
            
    improvement = round(((current_week_count - previous_week_count) / 7.0) * 100, 1)
    if improvement > 0:
        insights.append({
            "category": "Consistency",
            "title": "Habit Building",
            "message": f"Awesome! Your logging consistency improved by {improvement}% compared to last week. Building a routine is the first step to success.",
            "type": "success"
        })
    elif current_week_count == 7:
        insights.append({
            "category": "Consistency",
            "title": "Streak Master",
            "message": "Perfect consistency! You logged your food every single day this week. You are building an incredible habit.",
            "type": "success"
        })
    else:
        insights.append({
            "category": "Consistency",
            "title": "Consistency Check",
            "message": f"You logged food on {current_week_count} days this week. Try setting a reminder to log your meals every day.",
            "type": "info"
        })

    # 4. Water Intake Insight (last 7 days)
    water_met_count = 0
    for i in range(7):
        d = today - timedelta(days=i)
        if daily_water.get(d, 0) >= water_goal:
            water_met_count += 1

    if water_met_count > 0:
        insights.append({
            "category": "Hydration",
            "title": "Hydration Levels",
            "message": f"You reached your daily hydration goal ({water_goal}ml) {water_met_count} times this week. Hydration helps boost metabolism and energy levels!",
            "type": "success" if water_met_count >= 5 else "info"
        })

    # 5. Workout Calorie Burn (last 7 days)
    workout_count = 0
    total_burned = 0.0
    for i in range(7):
        d = today - timedelta(days=i)
        if d in daily_exercise:
            workout_count += 1
            total_burned += daily_exercise[d]

    if workout_count > 0:
        insights.append({
            "category": "Fitness",
            "title": "Active Energy",
            "message": f"You burned a total of {round(total_burned, 1)} kcal across {workout_count} workout(s) this week. This is a massive boost to your net calorie deficit!",
            "type": "success"
        })

    # 6. Protein Target (last 7 days)
    total_protein_7 = 0.0
    logged_protein_days_7 = 0
    for i in range(7):
        d = today - timedelta(days=i)
        if d in daily_protein:
            total_protein_7 += daily_protein[d]
            logged_protein_days_7 += 1

    if logged_protein_days_7 > 0:
        avg_protein = round(total_protein_7 / logged_protein_days_7, 1)
        if avg_protein < protein_goal * 0.8:
            insights.append({
                "category": "Nutrition",
                "title": "Protein Check",
                "message": f"Your average protein intake ({avg_protein}g) is below your target ({protein_goal}g). Try adding protein-rich foods like chicken, eggs, paneer, or lentils.",
                "type": "warning"
            })
        else:
            insights.append({
                "category": "Nutrition",
                "title": "Protein Fuel",
                "message": f"Excellent! You averaged {avg_protein}g of protein daily this week, meeting your body's recovery and muscle-building needs.",
                "type": "success"
            })

    return insights
