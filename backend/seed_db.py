# backend/seed_db.py
import os
import requests
from sqlalchemy.orm import Session
from datetime import date
from app.db import SessionLocal
from app.models import (
    User,
    Preference,
    Restriction,
    FoodItem,
    Category,
    Meal,
    MealPlan,
)

# -----------------------------
# USDA API Setup
# -----------------------------
USE_REAL_NUTRITION_API = True

USDA_API_KEY = os.getenv("USDA_API_KEY", "")
USDA_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"


def fetch_nutrition(food_name: str):
    """Fetch calories, protein, carbs, fat using USDA FoodData Central API."""
    if not USE_REAL_NUTRITION_API or not USDA_API_KEY:
        return None

    params = {
        "query": food_name,
        "pageSize": 1,
        "api_key": USDA_API_KEY,
    }

    try:
        response = requests.get(USDA_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if "foods" not in data or len(data["foods"]) == 0:
            print(f"⚠ USDA: No results for {food_name}")
            return None

        food = data["foods"][0]
        nutrients = {n["nutrientName"].lower(): n["value"] for n in food.get("foodNutrients", [])}

        return {
            "calories": nutrients.get("energy", 0),
            "protein": nutrients.get("protein", 0),
            "carbohydrate, by difference": nutrients.get("carbohydrate, by difference", 0),
            "total lipid (fat)": nutrients.get("total lipid (fat)", 0),
        }

    except Exception as e:
        print(f"⚠ USDA API error for {food_name}: {e}")
        return None


# ---------------------------------------------------------
# Static Data (fallback values are overwritten by USDA API)
# ---------------------------------------------------------
USERS = [
    {"username": "testuser", "email": "test@example.com", "password": "password123"},
]

CATEGORIES = ["Fruit", "Vegetable", "Grain", "Protein", "Nut", "Dairy"]

FOOD_ITEMS = [
    {"name": "Banana", "category": "Fruit"},
    {"name": "Oatmeal", "category": "Grain"},
    {"name": "Chicken Breast", "category": "Protein"},
    {"name": "Broccoli", "category": "Vegetable"},
    {"name": "Almonds", "category": "Nut"},
    {"name": "Greek Yogurt", "category": "Dairy"},
]

MEALS = [
    {"name": "Oatmeal Breakfast", "meal_type": "breakfast", "foods": ["Oatmeal", "Banana"]},
    {"name": "Chicken Lunch", "meal_type": "lunch", "foods": ["Chicken Breast", "Broccoli"]},
    {"name": "Snack Nuts", "meal_type": "snack", "foods": ["Almonds"]},
    {"name": "Chicken Dinner", "meal_type": "dinner", "foods": ["Chicken Breast", "Broccoli"]},
]

PREFERENCES = [
    {"key": "calorie_goal", "value": "2000"},
    {"key": "diet", "value": "balanced"},
]


# -----------------------------
# Seeder
# -----------------------------
def seed_db():
    db: Session = SessionLocal()
    try:
        print("Seeding database...")

        # --- Users ---
        user_map = {}
        for u in USERS:
            user = db.query(User).filter_by(email=u["email"]).first()
            if not user:
                user = User(**u)
                db.add(user)
                db.commit()
                db.refresh(user)
            user_map[user.username] = user
        print(f"Users: {list(user_map.keys())}")

        # --- Categories ---
        category_map = {}
        for c_name in CATEGORIES:
            category = db.query(Category).filter_by(name=c_name).first()
            if not category:
                category = Category(name=c_name)
                db.add(category)
                db.commit()
                db.refresh(category)
            category_map[c_name] = category

        # --- Food Items ---
        food_map = {}
        for f in FOOD_ITEMS:

            category_name = f["category"]
            category_obj = category_map[category_name]

            # Nutrition from USDA
            nutrition = fetch_nutrition(f["name"])
            if nutrition:
                calories = nutrition.get("calories", 0)
                protein = nutrition.get("protein", 0)
                carbs = nutrition.get("carbohydrate, by difference", 0)
                fat = nutrition.get("total lipid (fat)", 0)
            else:
                # fallback when API fails
                calories = protein = carbs = fat = 0

            food = db.query(FoodItem).filter_by(name=f["name"]).first()
            if not food:
                food = FoodItem(
                    name=f["name"],
                    calories=calories,
                    protein=protein,
                    carbs=carbs,
                    fat=fat,
                )
                food.category = category_obj
                db.add(food)
                db.commit()
                db.refresh(food)

            food_map[food.name] = food

            print(f"Added FoodItem: {food.name} ({calories} kcal)")

        # --- Meals ---
        meal_map = {}
        for m in MEALS:
            meal = db.query(Meal).filter_by(name=m["name"]).first()
            if not meal:
                meal = Meal(name=m["name"], meal_type=m["meal_type"])
                for food_name in m["foods"]:
                    meal.food_items.append(food_map[food_name])
                db.add(meal)
                db.commit()
                db.refresh(meal)
            meal_map[meal.name] = meal
        print(f"Meals: {list(meal_map.keys())}")

        # --- Preferences ---
        for user in user_map.values():
            for pref in PREFERENCES:
                existing = db.query(Preference).filter_by(user_id=user.id, key=pref["key"]).first()
                if not existing:
                    p = Preference(user_id=user.id, key=pref["key"], value=pref["value"])
                    db.add(p)
        db.commit()
        print("Preferences added.")

        # --- Restriction example (testing) ---
        almonds = food_map.get("Almonds")
        test_user = user_map.get("testuser")
        if almonds and test_user:
            existing = db.query(Restriction).filter_by(
                user_id=test_user.id,
                food_item_id=almonds.id
            ).first()
            if not existing:
                db.add(Restriction(user_id=test_user.id, food_item_id=almonds.id))
        db.commit()
        print("Restrictions added.")

        # --- Meal plan sample for today ---
        for user in user_map.values():
            meal_plan = db.query(MealPlan).filter_by(user_id=user.id, date=date.today()).first()
            if not meal_plan:
                meal_plan = MealPlan(user_id=user.id, date=date.today())
                for meal in meal_map.values():
                    meal_plan.meals.append(meal)
                db.add(meal_plan)
                db.commit()

        print("MealPlans added.")

        print("Database seeding complete!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
