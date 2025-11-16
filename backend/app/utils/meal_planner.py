# app/utils/meal_planner.py
from datetime import date
from typing import List, Optional
import random
from sqlalchemy.orm import Session
from app.models import (
    User,
    Meal,
    FoodItem,
    MealPlan,
    UserFoodHistory,
    Restriction,
    meal_food_association,
    mealplan_meals_association,
)

class MealPlanner:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def get_user_restrictions(self) -> List[int]:
        restricted = (
            self.db.query(Restriction.food_item_id)
            .filter(Restriction.user_id == self.user_id)
            .all()
        )
        return [r[0] for r in restricted]

    def get_removed_food_items(self) -> List[int]:
        removed = (
            self.db.query(UserFoodHistory.food_item_id)
            .filter(
                UserFoodHistory.user_id == self.user_id,
                UserFoodHistory.removed_count >= 5,
            )
            .all()
        )
        return [r[0] for r in removed]

    def mark_removed(self, food_item_id: int):
        history = (
            self.db.query(UserFoodHistory)
            .filter(
                UserFoodHistory.user_id == self.user_id,
                UserFoodHistory.food_item_id == food_item_id,
            )
            .first()
        )
        if not history:
            history = UserFoodHistory(
                user_id=self.user_id, food_item_id=food_item_id, removed_count=1
            )
            self.db.add(history)
        else:
            history.removed_count += 1
        self.db.commit()

        if history.removed_count >= 5:
            exists = (
                self.db.query(Restriction)
                .filter(
                    Restriction.user_id == self.user_id,
                    Restriction.food_item_id == food_item_id,
                )
                .first()
            )
            if not exists:
                restriction = Restriction(
                    user_id=self.user_id, food_item_id=food_item_id
                )
                self.db.add(restriction)
                self.db.commit()

    def suggest_meals(
        self,
        calorie_goal: Optional[int] = None,
        macros_goal: Optional[dict] = None,
    ) -> MealPlan:
        restricted_ids = set(self.get_user_restrictions() + self.get_removed_food_items())

        meals = (
            self.db.query(Meal)
            .join(Meal.food_items)
            .filter(~FoodItem.id.in_(restricted_ids))
            .all()
        )

        meal_plan = MealPlan(user_id=self.user_id, date=date.today())
        self.db.add(meal_plan)
        self.db.commit()  # commit to get meal_plan.id

        types = ["breakfast", "lunch", "dinner", "snack"]
        for meal_type in types:
            candidates = [m for m in meals if m.meal_type == meal_type]
            if candidates:
                selected = random.choice(candidates)
                meal_plan.meals.append(selected)

        self.db.commit()
        self.db.refresh(meal_plan)
        return meal_plan

    def export_shopping_list(self, meal_plan: MealPlan) -> dict:
        """
        Build a shopping list for all food items in the given meal plan.
        Returns a dictionary with food item names as keys and details as values.
        """
        shopping_items = {}
        for meal in meal_plan.meals:
            for item in meal.food_items:
                if not item.name:
                    continue  # Skip if name is None
                category_name = item.category.name if item.category else "Unknown"
                if item.name not in shopping_items:
                    shopping_items[item.name] = {
                        "category": category_name,
                        "quantity": 1
                    }
                else:
                    shopping_items[item.name]["quantity"] += 1
        return shopping_items
