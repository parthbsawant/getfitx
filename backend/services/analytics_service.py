from datetime import datetime, timedelta
import pytz
from config.db import db
from models.food_model import get_foods_by_user
from models.weight_model import get_weights_by_user
from models.exercise_model import get_exercises_by_user

IST = pytz.timezone("Asia/Kolkata")
users_collection = db["users"]

def get_calorie_analytics(user_id):
    foods = get_foods_by_user(user_id)
    now_ist = datetime.now(IST)
    
    # 30-day date sequence: from 29 days ago to today
    dates_list = [(now_ist - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(29, -1, -1)]
    daily_calories = {date: 0.0 for date in dates_list}
    
    for food in foods:
        consumed_at = food.get("consumedAt")
        if not consumed_at:
            continue
        date_str = consumed_at.astimezone(IST).strftime("%Y-%m-%d")
        if date_str in daily_calories:
            daily_calories[date_str] += food.get("calories", 0)

    chart_data = [{"date": d, "calories": round(daily_calories[d], 2)} for d in dates_list]
    
    # Calculations
    total_intake = sum(daily_calories.values())
    average_intake = round(total_intake / 30.0, 2)
    
    highest_day = max(chart_data, key=lambda x: x["calories"])
    lowest_day = min(chart_data, key=lambda x: x["calories"])
    
    return {
        "last30DaysCalories": chart_data,
        "averageIntake": average_intake,
        "highestCalorieDay": highest_day,
        "lowestCalorieDay": lowest_day,
        "chartData": chart_data
    }

def get_fat_loss_analytics(user_id):
    user = users_collection.find_one({"email": user_id})
    maintenance_calories = 2000.0
    goal_weight = 0.0
    starting_weight = 0.0
    current_weight = 0.0
    
    if user:
        maintenance_calories = user.get("maintenanceCalories", 2000.0)
        goal_weight = user.get("goalWeight", 0.0)
        starting_weight = user.get("weight", 0.0)

    # Get weight history to determine actual starting & current weight
    weights = get_weights_by_user(user_id)
    if weights:
        weights.sort(key=lambda x: x["loggedAt"])
        starting_weight = weights[0].get("weight", starting_weight)
        current_weight = weights[-1].get("weight", current_weight)
    else:
        current_weight = starting_weight

    foods = get_foods_by_user(user_id)
    exercises = get_exercises_by_user(user_id)
    
    # Group food and exercise by date YYYY-MM-DD in IST
    daily_food = {}
    for food in foods:
        consumed_at = food.get("consumedAt")
        if not consumed_at:
            continue
        date_str = consumed_at.astimezone(IST).strftime("%Y-%m-%d")
        daily_food[date_str] = daily_food.get(date_str, 0.0) + food.get("calories", 0)

    daily_exercise = {}
    for ex in exercises:
        logged_at = ex.get("loggedAt")
        if not logged_at:
            continue
        date_str = logged_at.astimezone(IST).strftime("%Y-%m-%d")
        daily_exercise[date_str] = daily_exercise.get(date_str, 0.0) + ex.get("caloriesBurned", 0)

    # Combine logged dates
    logged_dates = set(daily_food.keys()).union(set(daily_exercise.keys()))
    
    # Calculate daily deficit/surplus on all logged days
    cumulative_deficit = 0.0
    for date_str in logged_dates:
        food_cal = daily_food.get(date_str, 0.0)
        ex_cal = daily_exercise.get(date_str, 0.0)
        net_cal = food_cal - ex_cal
        deficit = maintenance_calories - net_cal
        cumulative_deficit += deficit

    # Calculate weekly (last 7 days) and monthly (last 30 days) deficit
    now_ist = datetime.now(IST)
    weekly_deficit = 0.0
    monthly_deficit = 0.0
    
    for i in range(7):
        date_str = (now_ist - timedelta(days=i)).strftime("%Y-%m-%d")
        food_cal = daily_food.get(date_str, 0.0)
        ex_cal = daily_exercise.get(date_str, 0.0)
        net_cal = food_cal - ex_cal
        # Deficit is relative to maintenance calories
        # If they logged nothing on a day, we assume 0 deficit rather than maintenance
        if date_str in logged_dates:
            weekly_deficit += (maintenance_calories - net_cal)
            
    for i in range(30):
        date_str = (now_ist - timedelta(days=i)).strftime("%Y-%m-%d")
        food_cal = daily_food.get(date_str, 0.0)
        ex_cal = daily_exercise.get(date_str, 0.0)
        net_cal = food_cal - ex_cal
        if date_str in logged_dates:
            monthly_deficit += (maintenance_calories - net_cal)

    estimated_fat_lost = round(cumulative_deficit / 7700.0, 2)
    weekly_fat_loss = round(weekly_deficit / 7700.0, 2)
    monthly_fat_loss = round(monthly_deficit / 7700.0, 2)
    
    # Progress toward weight goal
    progress_percentage = 0.0
    if starting_weight > goal_weight and goal_weight > 0:
        target_loss = starting_weight - goal_weight
        progress_percentage = round((estimated_fat_lost / target_loss) * 100, 2)

    return {
        "cumulativeDeficit": round(cumulative_deficit, 2),
        "estimatedFatLostKg": max(0.0, estimated_fat_lost),
        "weeklyFatLossKg": round(max(0.0, weekly_fat_loss), 2),
        "monthlyFatLossKg": round(max(0.0, monthly_fat_loss), 2),
        "progressPercentage": max(0.0, progress_percentage),
        "startingWeight": starting_weight,
        "currentWeight": current_weight,
        "goalWeight": goal_weight
    }

def get_meal_distribution_analytics(user_id):
    foods = get_foods_by_user(user_id)
    
    # Filter foods in the last 30 days
    now_ist = datetime.now(IST)
    thirty_days_ago = now_ist - timedelta(days=30)
    
    meal_calories = {"breakfast": 0.0, "lunch": 0.0, "dinner": 0.0, "snacks": 0.0}
    meal_protein = {"breakfast": 0.0, "lunch": 0.0, "dinner": 0.0, "snacks": 0.0}
    meal_carbs = {"breakfast": 0.0, "lunch": 0.0, "dinner": 0.0, "snacks": 0.0}
    meal_fats = {"breakfast": 0.0, "lunch": 0.0, "dinner": 0.0, "snacks": 0.0}
    
    for food in foods:
        consumed_at = food.get("consumedAt")
        if not consumed_at or consumed_at.astimezone(IST) < thirty_days_ago:
            continue
            
        # Normalize meal type
        meal_type = food.get("mealType", "snacks").lower().strip()
        if "breakfast" in meal_type:
            key = "breakfast"
        elif "lunch" in meal_type:
            key = "lunch"
        elif "dinner" in meal_type:
            key = "dinner"
        else:
            key = "snacks"
            
        calories = food.get("calories", 0.0)
        meal_calories[key] += calories
        meal_protein[key] += food.get("protein", 0.0)
        meal_carbs[key] += food.get("carbs", 0.0)
        meal_fats[key] += food.get("fats", 0.0)

    total_calories = sum(meal_calories.values())
    
    meal_percentages = {}
    for key in meal_calories:
        meal_percentages[key] = round((meal_calories[key] / total_calories) * 100, 2) if total_calories > 0 else 0.0

    insights = {}
    for key in meal_calories:
        insights[key] = {
            "calories": round(meal_calories[key], 2),
            "protein": round(meal_protein[key], 2),
            "carbs": round(meal_carbs[key], 2),
            "fats": round(meal_fats[key], 2)
        }

    return {
        "mealDistribution": meal_percentages,
        "nutritionInsights": insights,
        "totalCalories30Days": round(total_calories, 2)
    }

def get_macro_analytics(user_id):
    user = users_collection.find_one({"email": user_id})
    target_calories = 2000.0
    
    if user:
        target_calories = user.get("targetCalories", user.get("maintenanceCalories", 2000.0))
        if target_calories <= 0:
            target_calories = 2000.0
            
    # Macro goals (explicit or dynamic defaults: 30% P, 40% C, 30% F)
    protein_goal = user.get("proteinGoal") if user and user.get("proteinGoal") else int((target_calories * 0.30) / 4)
    carb_goal = user.get("carbGoal") if user and user.get("carbGoal") else int((target_calories * 0.40) / 4)
    fat_goal = user.get("fatGoal") if user and user.get("fatGoal") else int((target_calories * 0.30) / 9)
    
    # Query today's food logs
    foods = get_foods_by_user(user_id)
    now_ist = datetime.now(IST)
    today_str = now_ist.strftime("%Y-%m-%d")
    
    today_protein = 0.0
    today_carbs = 0.0
    today_fats = 0.0
    today_calories = 0.0
    
    for food in foods:
        consumed_at = food.get("consumedAt")
        if not consumed_at:
            continue
        date_str = consumed_at.astimezone(IST).strftime("%Y-%m-%d")
        if date_str == today_str:
            today_protein += food.get("protein", 0.0)
            today_carbs += food.get("carbs", 0.0)
            today_fats += food.get("fats", 0.0)
            today_calories += food.get("calories", 0.0)

    # Percentage progress
    protein_progress = round((today_protein / protein_goal) * 100, 2) if protein_goal > 0 else 0.0
    carb_progress = round((today_carbs / carb_goal) * 100, 2) if carb_goal > 0 else 0.0
    fat_progress = round((today_fats / fat_goal) * 100, 2) if fat_goal > 0 else 0.0
    
    # Actual distribution splits based on calories
    p_cal = today_protein * 4.0
    c_cal = today_carbs * 4.0
    f_cal = today_fats * 9.0
    total_macro_calories = p_cal + c_cal + f_cal
    
    protein_split = round((p_cal / total_macro_calories) * 100, 2) if total_macro_calories > 0 else 0.0
    carb_split = round((c_cal / total_macro_calories) * 100, 2) if total_macro_calories > 0 else 0.0
    fat_split = round((f_cal / total_macro_calories) * 100, 2) if total_macro_calories > 0 else 0.0

    # Macro history (last 7 days)
    dates_7 = [(now_ist - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
    history_data = {d: {"protein": 0.0, "carbs": 0.0, "fats": 0.0, "calories": 0.0} for d in dates_7}
    
    for food in foods:
        consumed_at = food.get("consumedAt")
        if not consumed_at:
            continue
        date_str = consumed_at.astimezone(IST).strftime("%Y-%m-%d")
        if date_str in history_data:
            history_data[date_str]["protein"] += food.get("protein", 0.0)
            history_data[date_str]["carbs"] += food.get("carbs", 0.0)
            history_data[date_str]["fats"] += food.get("fats", 0.0)
            history_data[date_str]["calories"] += food.get("calories", 0.0)
            
    history_list = []
    protein_deficiency_days = 0
    for d in dates_7:
        day_stats = history_data[d]
        history_list.append({
            "date": d,
            "protein": round(day_stats["protein"], 2),
            "carbs": round(day_stats["carbs"], 2),
            "fats": round(day_stats["fats"], 2),
            "calories": round(day_stats["calories"], 2)
        })
        # If the day had any logging (calories > 0) but protein was deficient (< 80% of goal)
        if day_stats["calories"] > 0 and day_stats["protein"] < (protein_goal * 0.8):
            protein_deficiency_days += 1
            
    # Protein deficiency alert
    protein_alert = False
    protein_alert_message = ""
    if today_protein < (protein_goal * 0.8) and now_ist.hour >= 18: # late in the day (after 6 PM)
        protein_alert = True
        protein_alert_message = f"Your protein intake today is deficient ({round(today_protein, 1)}g vs goal of {protein_goal}g). Consider having a protein-rich snack."
    elif protein_deficiency_days >= 3:
        protein_alert = True
        protein_alert_message = f"You fell short of your protein goal on {protein_deficiency_days} of the last 7 days. Focus on protein sources."

    return {
        "todayMacros": {
            "protein": round(today_protein, 2),
            "carbs": round(today_carbs, 2),
            "fats": round(today_fats, 2),
            "calories": round(today_calories, 2)
        },
        "macroGoals": {
            "proteinGoal": protein_goal,
            "carbGoal": carb_goal,
            "fatGoal": fat_goal
        },
        "progressPercentage": {
            "protein": protein_progress,
            "carbs": carb_progress,
            "fats": fat_progress
        },
        "macroSplits": {
            "protein": protein_split,
            "carbs": carb_split,
            "fats": fat_split
        },
        "history7Days": history_list,
        "proteinAlert": {
            "isDeficient": protein_alert,
            "message": protein_alert_message
        }
    }
