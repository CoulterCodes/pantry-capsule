# backend/test_meal_plan.py
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import User
from app.utils.meal_planner import MealPlanner

def main():
    db: Session = SessionLocal()

    try:
        # Get first user from DB (or create one if none exists)
        user = db.query(User).first()
        if not user:
            print("No users found in the database. Please seed a user first.")
            return

        print(f"Using user: {user.username} (ID: {user.id})")

        # Initialize MealPlanner
        planner = MealPlanner(db, user.id)
        week_plan = planner.suggest_multi_day_meals(days=7)

        # Generate meal plan
        meal_plan = planner.suggest_meals()

        # Multi-day test
        for day_plan in week_plan:
            print(f"\n=== {day_plan.date} ===")
            for meal in day_plan.meals:
                foods = ", ".join(f.name for f in meal.food_items)
                print(f"{meal.meal_type.capitalize()}: {meal.name} - {foods}")

        # Generate shopping list
        shopping_list = planner.export_shopping_list(meal_plan)

        # Print results
        print("\n=== Meal Plan ===")
        for meal in meal_plan.meals:
            print(f"\n{meal.meal_type.capitalize()}: {meal.name}")
            for item in meal.food_items:
                category_name = item.category.name if item.category else "Unknown"
                print(f"  - {item.name} ({category_name})")

            for recipe in meal.recipes:
                print(f"  Recipe: {recipe.name}")
                for ingredient in recipe.ingredients:
                    print(f"    - {ingredient.food_item.name}: {ingredient.quantity}")

        print("\n=== Shopping List ===")
        for name, info in shopping_list.items():
            print(f"{name} ({info['category']}): {info['quantity']}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
