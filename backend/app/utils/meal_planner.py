# app/utils/meal_planner.py
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import (
    User,
    Meal,
    FoodItem,
    MealPlan,
    MealPlanMeal,
    UserFoodHistory,
    Restriction,
)

class MealPlanner:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def get_user_restrictions(self) -> List[int]:
        """Return list of food_item_ids the user cannot have."""
        restricted = (
            self.db.query(Restriction.food_item_id)
            .filter(Restriction.user_id == self.user_id)
            .all()
        )
        return [r[0] for r in restricted]

    def get_removed_food_items(self) -> List[int]:
        """Return food items that the user repeatedly removed."""
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
        """Increment removed_count or create UserFoodHistory if not exists."""
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

        # Automatically add to restrictions after 5 removals
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
        macros_goal: Optional[dict] = None,  # {"protein": 100, "carbs": 150, "fat": 50}
    ) -> MealPlan:
        """Generate a meal plan respecting user restrictions."""
        restricted_ids = set(self.get_user_restrictions() + self.get_removed_food_items())

        # Fetch all meals that do not contain restricted items
        meals = (
            self.db.query(Meal)
            .join(Meal.food_items)
            .filter(~FoodItem.id.in_(restricted_ids))
            .all()
        )

        # Simple naive selection: pick one breakfast, lunch, dinner, snack
        meal_plan = MealPlan(user_id=self.user_id, date=date.today())
        self.db.add(meal_plan)
        self.db.commit()  # commit to get meal_plan.id

        types = ["breakfast", "lunch", "dinner", "snack"]
        for meal_type in types:
            candidates = [m for m in meals if m.meal_type == meal_type]
            if candidates:
                selected = candidates[0]  # pick the first for now
                association = MealPlanMeal(mealplan_id=meal_plan.id, meal_id=selected.id)
                self.db.add(association)

        self.db.commit()
        self.db.refresh(meal_plan)
        return meal_plan

    def export_shopping_list(self, meal_plan: MealPlan) -> List[str]:
        """Return a list of food item names from the meal plan."""
        items = (
            self.db.query(FoodItem.name)
            .join(MealFood, MealFood.food_item_id == FoodItem.id)
            .join(MealPlanMeal, MealPlanMeal.meal_id == MealFood.meal_id)
            .filter(MealPlanMeal.mealplan_id == meal_plan.id)
            .all()
        )
        return [i[0] for i in items]
