import google.generativeai as genai
from PIL import Image
import json
import io
import re
from app.config import settings

genai.configure(api_key=settings.gemini_api_key)

FOOD_DETECTION_PROMPT = """
You are a specialized Indian food recognition AI. Analyze this food image and identify all dishes present.

Return ONLY valid JSON in this exact format:
{
  "foods": [
    {
      "name": "masala_dosa",
      "display_name": "Masala Dosa",
      "confidence": 0.95,
      "category": "south_indian"
    }
  ],
  "meal_context": "south_indian_breakfast"
}

Rules:
- Use snake_case for name field (used for INDB lookup)
- Be specific: "masala_dosa" not just "dosa"
- Include confidence 0.0-1.0
- List ALL dishes visible (including sides like sambar, chutney)
- If unclear, use your best guess with lower confidence
- Categories: south_indian, north_indian, rice_dish, bread, snack, beverage, dessert, curry, salad
"""

QUESTION_GENERATION_PROMPT = """
You are a nutrition expert specializing in Indian cuisine. Generate smart follow-up questions to accurately calculate nutrition.

Food detected: {foods}

Generate exactly 3 questions maximum. Return ONLY valid JSON:
{{
  "questions": [
    {{
      "id": "q1",
      "question": "How many {food_name} did you eat?",
      "options": ["Half", "One", "Two", "More than two"],
      "food_name": "{food_name}"
    }},
    {{
      "id": "q2",
      "question": "Was it homemade or restaurant?",
      "options": ["Homemade (light oil)", "Restaurant (regular)", "Restaurant (street food)"],
      "food_name": "{food_name}"
    }},
    {{
      "id": "q3",
      "question": "How much chutney/sambar did you have?",
      "options": ["None", "Small portion", "Regular portion", "Extra"],
      "food_name": "accompaniments"
    }}
  ]
}}

Rules:
- Questions must be specific to the detected food
- Options must be 2-4 choices maximum
- Focus on: quantity, cooking method, accompaniments
- Question text must be natural and conversational
"""


async def detect_foods(image_bytes: bytes) -> dict:
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    image = Image.open(io.BytesIO(image_bytes))

    response = model.generate_content([FOOD_DETECTION_PROMPT, image])
    text = response.text.strip()

    # Extract JSON from response
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())

    # Fallback structure
    return {
        "foods": [{"name": "unknown_dish", "display_name": "Indian Dish", "confidence": 0.5, "category": "unknown"}],
        "meal_context": "unknown"
    }


async def generate_questions_ai(foods: list[str]) -> dict:
    model = genai.GenerativeModel("gemini-2.0-flash-exp")

    food_names = ", ".join(foods)
    primary_food = foods[0] if foods else "dish"
    display_food = primary_food.replace("_", " ").title()

    prompt = QUESTION_GENERATION_PROMPT.format(
        foods=food_names,
        food_name=display_food
    )

    response = model.generate_content(prompt)
    text = response.text.strip()

    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())

    # Fallback questions
    return {
        "questions": [
            {
                "id": "q1",
                "question": f"How much {display_food} did you eat?",
                "options": ["Small portion (half plate)", "Regular portion (one plate)", "Large portion (two plates)"],
                "food_name": display_food
            },
            {
                "id": "q2",
                "question": "Where was this meal prepared?",
                "options": ["Homemade (light oil)", "Restaurant", "Street food/dhaba"],
                "food_name": display_food
            },
            {
                "id": "q3",
                "question": "Did you have any accompaniments?",
                "options": ["No extras", "Chutney only", "Sambar + chutney", "Full set with rice"],
                "food_name": "accompaniments"
            }
        ]
    }
