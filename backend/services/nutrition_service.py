import json
import requests
import os

from dotenv import load_dotenv

load_dotenv()


# USDA CONFIG
USDA_API_KEY = os.getenv("USDA_API_KEY")

BASE_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"


# LOAD INDIAN FOOD DATABASE
with open(
    "data/indian_foods.json",
    "r",
    encoding="utf-8"
) as file:

    indian_foods = json.load(file)


# ---------------------------------------------------
# SEARCH INDIAN FOOD DATABASE
# ---------------------------------------------------

def search_indian_foods(query):

    query = query.lower().strip()

    matched_foods = []

    for food in indian_foods:

        food_name = food.get(
            "foodName",
            ""
        ).lower()

        aliases = [
            alias.lower()
            for alias in food.get(
                "aliases",
                []
            )
        ]

        # DIRECT FOOD NAME MATCH
        if query in food_name:

            matched_foods.append(food)
            continue

        # ALIAS MATCH
        for alias in aliases:

            if query in alias:

                matched_foods.append(food)
                break

    return matched_foods


# ---------------------------------------------------
# SEARCH FOOD
# PRIORITY:
# 1. LOCAL INDIAN DB
# 2. USDA API
# ---------------------------------------------------

def search_food(query):

    try:

        # -------------------------------------------
        # STEP 1 — SEARCH LOCAL INDIAN DB
        # -------------------------------------------

        local_results = search_indian_foods(query)

        if local_results:

            return local_results

        # -------------------------------------------
        # STEP 2 — USDA FALLBACK
        # -------------------------------------------

        params = {

            "query": query,

            "api_key": USDA_API_KEY,

            "pageSize": 10
        }

        response = requests.get(
            BASE_URL,
            params=params
        )

        data = response.json()

        foods = data.get("foods", [])

        formatted_results = []

        for food in foods:

            nutrients = food.get(
                "foodNutrients",
                []
            )

            calories = 0
            protein = 0
            carbs = 0
            fats = 0

            # EXTRACT NUTRIENTS
            for nutrient in nutrients:

                nutrient_name = nutrient.get(
                    "nutrientName",
                    ""
                ).lower()

                value = nutrient.get(
                    "value",
                    0
                )

                # CALORIES
                if "energy" in nutrient_name:

                    calories = value

                # PROTEIN
                elif "protein" in nutrient_name:

                    protein = value

                # CARBS
                elif "carbohydrate" in nutrient_name:

                    carbs = value

                # FATS
                elif "total lipid" in nutrient_name:

                    fats = value

            formatted_results.append({

                "foodName":
                    food.get("description"),

                "aliases": [],

                "category":
                    "external",

                "cuisineType":
                    "unknown",

                "region": [],

                "veg":
                    True,

                "servingOptions": [

                    {

                        "name":
                            str(
                                food.get(
                                    "servingSize",
                                    "100g"
                                )
                            ),

                        "grams":
                            food.get(
                                "servingSize",
                                100
                            ),

                        "calories":
                            round(calories, 2),

                        "protein":
                            round(protein, 2),

                        "carbs":
                            round(carbs, 2),

                        "fats":
                            round(fats, 2)
                    }
                ],

                "tags": [],

                "glycemicIndex":
                    None,

                "source":
                    "usda_api"
            })

        return formatted_results

    except Exception as e:

        return {
            "error": str(e)
        }