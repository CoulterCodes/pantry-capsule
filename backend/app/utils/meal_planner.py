# app/utils/meal_planner.py
from datetime import date, timedelta
from typing import List, Optional
import random
from itertools import product
from sqlalchemy.orm import Session
from collections import defaultdict
from app.models import (
    User,
    Meal,
    FoodItem,
    MealPlan,
    UserFoodHistory,
    Restriction,
    Preference,
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

    def get_user_preferences(self):
        prefs = self.db.query(Preference).filter_by(user_id=self.user_id).all()
        return {p.key: p.value for p in prefs}

    # -------------------------------------------------
    #  CALCULATE NUTRITION TOTALS
    # -------------------------------------------------
    def _calculate_plan_nutrition(self, meal_plan: MealPlan):
        total_cal = total_p = total_c = total_f = 0
        for meal in meal_plan.meals:
            for item in meal.food_items:
                total_cal += item.calories or 0
                total_p += item.protein or 0
                total_c += item.carbs or 0
                total_f += item.fat or 0
        meal_plan.total_calories = total_cal
        meal_plan.total_protein = total_p
        meal_plan.total_carbs = total_c
        meal_plan.total_fat = total_f

    # -------------------------------------------------
    # SCORING MEALS BY MACROS
    # -------------------------------------------------
    def _score_meal(self, meal: Meal, target_macros: dict) -> float:
        total_p = sum(item.protein or 0 for item in meal.food_items)
        total_c = sum(item.carbs or 0 for item in meal.food_items)
        total_f = sum(item.fat or 0 for item in meal.food_items)
        total_cal = sum(item.calories or 0 for item in meal.food_items)

        if total_cal == 0:
            return float("inf")

        p_diff = abs((total_p * 4 / total_cal) - target_macros.get("protein_pct", 0.3))
        c_diff = abs((total_c * 4 / total_cal) - target_macros.get("carbs_pct", 0.4))
        f_diff = abs((total_f * 9 / total_cal) - target_macros.get("fat_pct", 0.3))

        return p_diff + c_diff + f_diff

    #------------------------------------------------------
    # Suggest Meals with Macro Scoring
    #------------------------------------------------------
    def suggest_meals(
        self,
        calorie_goal: Optional[int] = 2000,
        macros_goal: Optional[dict] = None,
        optimize_combinations: bool = True,
    ) -> MealPlan:
        if macros_goal is None:
            macros_goal = {
                "protein_pct": 0.3,
                "carbs_pct": 0.4,
                "fat_pct": 0.3,
                "calories": calorie_goal,
            }

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
        candidates_by_type = {meal_type: [m for m in meals if m.meal_type == meal_type] for meal_type in types}

        if optimize_combinations:
            combinations = product(
                candidates_by_type.get("breakfast", [None]),
                candidates_by_type.get("lunch", [None]),
                candidates_by_type.get("dinner", [None]),
                candidates_by_type.get("snack", [None]),
            )

            best_score = float("inf")
            best_combination = None
            for combo in combinations:
                combo_meals = [m for m in combo if m is not None]
                total_p = sum(sum(f.protein or 0 for f in m.food_items) for m in combo_meals)
                total_c = sum(sum(f.carbs or 0 for f in m.food_items) for m in combo_meals)
                total_f = sum(sum(f.fat or 0 for f in m.food_items) for m in combo_meals)
                total_cal = sum(sum(f.calories or 0 for f in m.food_items) for m in combo_meals)

                if total_cal == 0:
                    continue

                p_diff = abs((total_p * 4 / total_cal) - macros_goal.get("protein_pct", 0.3))
                c_diff = abs((total_c * 4 / total_cal) - macros_goal.get("carbs_pct", 0.4))
                f_diff = abs((total_f * 9 / total_cal) - macros_goal.get("fat_pct", 0.3))

                score = p_diff + c_diff + f_diff
                if score < best_score:
                    best_score = score
                    best_combination = combo_meals

            if best_combination:
                for m in best_combination:
                    meal_plan.meals.append(m)
        else:
            for meal_type in types:
                candidates = candidates_by_type.get(meal_type, [])
                if candidates:
                    scored = sorted(candidates, key=lambda m: self._score_meal(m, macros_goal))
                    meal_plan.meals.append(scored[0])

        self._calculate_plan_nutrition(meal_plan)
        self.db.commit()
        self.db.refresh(meal_plan)
        return meal_plan

    #--------------------------------------------
    # Suggesting Meals for Multiple Days
    #--------------------------------------------
    def suggest_multi_day_meals(
        self,
        days: int = 7,
        calorie_goal: Optional[int] = 2000,
        macros_goal: Optional[dict] = None,
        optimize_combinations: bool = True,
    ) -> List[MealPlan]:
        multi_day_plans = []
        used_meals = defaultdict(int)

        for day_offset in range(days):
            meal_plan = MealPlan(user_id=self.user_id, date=date.today() + timedelta(days=day_offset))
            self.db.add(meal_plan)
            self.db.commit()

            daily_plan = self.suggest_meals(
                calorie_goal=calorie_goal,
                macros_goal=macros_goal,
                optimize_combinations=optimize_combinations
            )

            meal_plan.meals = daily_plan.meals
            for m in daily_plan.meals:
                used_meals[m.id] += 1

            self.db.commit()
            self.db.refresh(meal_plan)
            multi_day_plans.append(meal_plan)

        return multi_day_plans

    #--------------------------------------------
    # Export Shopping List
    #--------------------------------------------
    def export_shopping_list(self, meal_plan: MealPlan) -> dict:
        shopping_items = {}
        for meal in meal_plan.meals:
            for item in meal.food_items:
                if not item.name:
                    continue
                category_name = item.category.name if item.category else "Unknown"
                if item.name not in shopping_items:
                    shopping_items[item.name] = {"category": category_name, "quantity": 1}
                else:
                    shopping_items[item.name]["quantity"] += 1
        return shopping_items
