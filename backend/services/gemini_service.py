import os
import json

from dotenv import load_dotenv
from google import genai

load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def estimate_food_nutrition(user_input):

    try:

        prompt = f"""
You are a nutrition estimation AI.

Estimate:
- calories
- protein
- carbs
- fats
- quantity

Return ONLY valid JSON.

Format:

{{
  "foods": [
    {{
      "foodName": "Poha",
      "quantity": "2 bowls",
      "calories": 480,
      "protein": 8,
      "carbs": 72,
      "fats": 14
    }}
  ],
  "totalCalories": 480
}}

USER INPUT:
{user_input}
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        raw_text = response.text.strip()

        raw_text = raw_text.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()

        parsed_json = json.loads(raw_text)

        return parsed_json

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }