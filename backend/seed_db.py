# backend/seed_db.py
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
# Seed Data
# -----------------------------
USERS = [
    {"username": "testuser", "email": "test@example.com", "password": "password123"},
]

CATEGORIES = ["Fruit", "Vegetable", "Grain", "Protein", "Nut", "Dairy"]

FOOD_ITEMS = [
    {"name": "Banana", "category": "Fruit", "calories": 100, "protein": 1, "carbs": 27, "fat": 0.3},
    {"name": "Oatmeal", "category": "Grain", "calories": 150, "protein": 5, "carbs": 27, "fat": 3},
    {"name": "Chicken Breast", "category": "Protein", "calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
    {"name": "Broccoli", "category": "Vegetable", "calories": 55, "protein": 3.7, "carbs": 11, "fat": 0.6},
    {"name": "Almonds", "category": "Nut", "calories": 170, "protein": 6, "carbs": 6, "fat": 15},
    {"name": "Greek Yogurt", "category": "Dairy", "calories": 100, "protein": 10, "carbs": 6, "fat": 0},
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
        print("🔄 Seeding database...")

        # --- Users ---
        user_map = {}
        for u in USERS:
            user = db.query(User).filter_by(email=u["email"]).first()
            if not user:
                user = User(**u)
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"🧑 Added user: {user.username}")
            else:
                print(f"🧑 User exists: {user.username}")
            user_map[user.username] = user

        # --- Categories ---
        category_map = {}
        for name in CATEGORIES:
            category = db.query(Category).filter_by(name=name).first()
            if not category:
                category = Category(name=name)
                db.add(category)
                db.commit()
                db.refresh(category)
                print(f"📦 Added category: {name}")
            category_map[name] = category

        # --- Food Items ---
        food_map = {}
        for item in FOOD_ITEMS:
            name = item["name"]
            category_name = item["category"]

            food = db.query(FoodItem).filter_by(name=name).first()
            if not food:
                food = FoodItem(
                    name=name,
                    calories=item["calories"],
                    protein=item["protein"],
                    carbs=item["carbs"],
                    fat=item["fat"],
                    category=category_map[category_name]
                )
                db.add(food)
                db.commit()
                db.refresh(food)
                print(f"🥗 Added food item: {name}")
            else:
                print(f"🥗 Food item exists: {name}")

            food_map[name] = food

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
                print(f"🍽 Added meal: {meal.name}")
            else:
                print(f"🍽 Meal exists: {meal.name}")
            meal_map[meal.name] = meal

        # --- Preferences ---
        for user in user_map.values():
            for pref in PREFERENCES:
                existing = db.query(Preference).filter_by(user_id=user.id, key=pref["key"]).first()
                if not existing:
                    p = Preference(user_id=user.id, **pref)
                    db.add(p)
            db.commit()
        print("⚙ Preferences added.")

        # --- Restrictions (example) ---
        almonds = food_map.get("Almonds")
        test_user = user_map.get("testuser")
        if almonds and test_user:
            exists = db.query(Restriction).filter_by(
                user_id=test_user.id, food_item_id=almonds.id
            ).first()
            if not exists:
                db.add(Restriction(user_id=test_user.id, food_item_id=almonds.id))
                db.commit()
                print("🚫 Restriction added: testuser → Almonds")

        # --- Meal Plan Example ---
        for user in user_map.values():
            meal_plan = db.query(MealPlan).filter_by(
                user_id=user.id, date=date.today()
            ).first()

            if not meal_plan:
                meal_plan = MealPlan(user_id=user.id, date=date.today())
                for meal in meal_map.values():
                    meal_plan.meals.append(meal)
                db.add(meal_plan)
                db.commit()
                print(f"📅 Meal plan created for {user.username}")
            else:
                print(f"📅 Meal plan already exists for {user.username}")

        print("\n✅ Database seeding complete!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
