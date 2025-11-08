from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.utils.meal_planner import MealPlanner
from app.models import MealPlan

router = APIRouter(prefix="/meal-planner", tags=["meal-planner"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/generate/{user_id}", response_model=dict)
def generate_meal_plan(user_id: int, db: Session = Depends(get_db)):
    planner = MealPlanner(db, user_id)
    meal_plan = planner.suggest_meals()
    shopping_list = planner.export_shopping_list(meal_plan)
    return {
        "meal_plan_id": meal_plan.id,
        "date": str(meal_plan.date),
        "shopping_list": shopping_list,
    }

@router.post("/remove-item/{user_id}/{food_item_id}")
def remove_food_item(user_id: int, food_item_id: int, db: Session = Depends(get_db)):
    planner = MealPlanner(db, user_id)
    planner.mark_removed(food_item_id)
    return {"message": f"Food item {food_item_id} marked as removed for user {user_id}"}
