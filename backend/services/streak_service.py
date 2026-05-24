from datetime import datetime, timedelta
import pytz
from config.db import db
from models.food_model import get_foods_by_user
from models.weight_model import get_weights_by_user

IST = pytz.timezone("Asia/Kolkata")
users_collection = db["users"]

def calculate_consecutive_streak(sorted_dates, today_date, allow_today_or_yesterday=True):
    if not sorted_dates:
        return 0, 0
        
    current_streak = 1
    longest_streak = 1
    
    for i in range(1, len(sorted_dates)):
        diff = (sorted_dates[i] - sorted_dates[i - 1]).days
        if diff == 1:
            current_streak += 1
            longest_streak = max(longest_streak, current_streak)
        elif diff > 1:
            current_streak = 1
            
    if allow_today_or_yesterday:
        last_date = sorted_dates[-1]
        diff_from_today = (today_date - last_date).days
        if diff_from_today > 1:
            current_streak = 0
            
    return current_streak, longest_streak

def get_advanced_streak_data(user_id):
    user = users_collection.find_one({"email": user_id})
    if not user:
        return None
        
    streak_freezes_available = user.get("streakFreezesAvailable", 1)
    frozen_dates_str = user.get("frozenDates", [])
    
    # Parse frozen dates
    frozen_dates = set()
    for fd in frozen_dates_str:
        try:
            frozen_dates.add(datetime.strptime(fd, "%Y-%m-%d").date())
        except ValueError:
            pass

    # 1. Get Food logging dates
    foods = get_foods_by_user(user_id)
    food_dates = set()
    for food in foods:
        consumed_at = food.get("consumedAt")
        if consumed_at:
            food_dates.add(consumed_at.astimezone(IST).date())
            
    # Combine food logging dates with frozen dates
    active_dates = sorted(food_dates.union(frozen_dates))
    
    now_ist = datetime.now(IST)
    today = now_ist.date()
    
    food_current_streak, food_longest_streak = calculate_consecutive_streak(active_dates, today)
    
    # Best month streak
    from collections import defaultdict
    by_month = defaultdict(list)
    for d in active_dates:
        by_month[(d.year, d.month)].append(d)
        
    best_month_streak = 0
    for key, month_dates in by_month.items():
        month_dates.sort()
        _, longest_in_month = calculate_consecutive_streak(month_dates, today, allow_today_or_yesterday=False)
        best_month_streak = max(best_month_streak, longest_in_month)
        
    if not active_dates:
        best_month_streak = 0
        
    # Monthly consistency %
    # Days in the current calendar month up to today
    current_year = today.year
    current_month = today.month
    total_days_in_month_so_far = today.day
    
    active_days_this_month = sum(
        1 for d in active_dates
        if d.year == current_year and d.month == current_month and d <= today
    )
    
    monthly_consistency = round((active_days_this_month / total_days_in_month_so_far) * 100, 2) if total_days_in_month_so_far > 0 else 0.0

    # 2. Calorie Goal Streak
    target_calories = user.get("targetCalories", 2000.0)
    # Find daily food intake
    daily_calories = defaultdict(float)
    for food in foods:
        consumed_at = food.get("consumedAt")
        if consumed_at:
            d = consumed_at.astimezone(IST).date()
            daily_calories[d] += food.get("calories", 0.0)
            
    calorie_adherence_dates = sorted([
        d for d, cal in daily_calories.items()
        if cal > 0 and cal <= target_calories
    ])
    
    calorie_current_streak, calorie_longest_streak = calculate_consecutive_streak(calorie_adherence_dates, today)

    # 3. Weight Logging Streak
    weights = get_weights_by_user(user_id)
    weight_dates = sorted(list(set([
        w.get("loggedAt").astimezone(IST).date()
        for w in weights if w.get("loggedAt")
    ])))
    
    weight_current_streak, weight_longest_streak = calculate_consecutive_streak(weight_dates, today)

    return {
        "foodStreak": {
            "currentStreak": food_current_streak,
            "longestStreak": food_longest_streak,
            "bestMonthStreak": best_month_streak,
            "monthlyConsistencyPercentage": monthly_consistency
        },
        "calorieGoalStreak": {
            "currentStreak": calorie_current_streak,
            "longestStreak": calorie_longest_streak
        },
        "weightStreak": {
            "currentStreak": weight_current_streak,
            "longestStreak": weight_longest_streak
        },
        "streakFreezeInfo": {
            "availableFreezes": streak_freezes_available,
            "frozenDates": sorted(list(frozen_dates_str))
        }
    }

def apply_streak_freeze(user_id, date_str):
    user = users_collection.find_one({"email": user_id})
    if not user:
        return False, "User not found"
        
    streak_freezes = user.get("streakFreezesAvailable", 1)
    if streak_freezes <= 0:
        return False, "No streak freezes available"
        
    frozen_dates = user.get("frozenDates", [])
    if date_str in frozen_dates:
        return False, "Date already frozen"
        
    # Apply freeze
    users_collection.update_one(
        {"email": user_id},
        {
            "$inc": {"streakFreezesAvailable": -1},
            "$push": {"frozenDates": date_str}
        }
    )
    return True, "Streak freeze applied successfully"

def add_streak_freezes(user_id, count):
    user = users_collection.find_one({"email": user_id})
    if not user:
        return False, "User not found"
        
    users_collection.update_one(
        {"email": user_id},
        {"$inc": {"streakFreezesAvailable": count}}
    )
    return True, f"Added {count} streak freezes successfully"
