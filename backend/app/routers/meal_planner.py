# backend/app/routers/meal_planner.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.utils.meal_planner import MealPlanner
from app.core import security
from app.models import MealPlan, User
from app.utils import schemas

router = APIRouter(prefix="/meal-planner", tags=["meal-planner"])

# ----------------------------
# Dependency to get DB
# ----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------
# Dependency to get current user from JWT
# ----------------------------
def get_current_user(
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = security.verify_access_token(token, credentials_exception)
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# ----------------------------
# Generate Meal Plan
# ----------------------------
@router.post("/generate", response_model=schemas.MealPlanOut)
def generate_meal_plan(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    planner = MealPlanner(db, current_user.id)
    meal_plan = planner.suggest_meals()
    shopping_list = planner.export_shopping_list(meal_plan)

    # Attach shopping list dynamically
    meal_plan.shopping_list = shopping_list

    # Eager load meals and their food items
    for meal in meal_plan.meals:
        meal.food_items  # relationship already defined in SQLAlchemy

    return meal_plan

# ----------------------------
# Remove Food Item
# ----------------------------
@router.post("/remove-item/{food_item_id}", response_model=dict)
def remove_food_item(
    food_item_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    planner = MealPlanner(db, current_user.id)
    planner.mark_removed(food_item_id)
    return {"message": f"Food item {food_item_id} marked as removed for user {current_user.id}"}
