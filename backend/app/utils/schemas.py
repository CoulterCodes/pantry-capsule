
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class PreferenceBase(BaseModel):
    name: str
    value: str

class PreferenceCreate(PreferenceBase):
    pass

class Preference(PreferenceBase):
    id: int
    owner_id: int
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    preferences: List[Preference] = []
    class Config:
        orm_mode = True

# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str

# ----------------------------
# Food Item in Shopping List
# ----------------------------
class FoodItemOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

# ----------------------------
# Meal Output
# ----------------------------
class MealOut(BaseModel):
    id: int
    name: str
    meal_type: str
    food_items: List[FoodItemOut]

    class Config:
        orm_mode = True

# ----------------------------
# Meal Plan Output
# ----------------------------
class MealPlanOut(BaseModel):
    id: int
    date: str
    meals: List[MealOut]
    shopping_list: List[str]  # optional, or could be List[FoodItemOut]

    class Config:
        orm_mode = True

# ----------------------------
# Food Item Response
# ----------------------------
class FoodItemOut(BaseModel):
    id: int
    name: str
    category: Optional[str]
    calories: Optional[float]
    protein: Optional[float]
    carbs: Optional[float]
    fat: Optional[float]
    tags: List[str] = []

    class Config:
        orm_mode = True

# ----------------------------
# Meal Response
# ----------------------------
class MealOut(BaseModel):
    id: int
    name: str
    meal_type: str
    food_items: List[FoodItemOut] = []

    class Config:
        orm_mode = True

# ----------------------------
# Meal Plan Response
# ----------------------------
class MealPlanOut(BaseModel):
    id: int
    user_id: int
    date: date
    meals: List[MealOut] = []
    shopping_list: List[FoodItemOut] = []

    class Config:
        orm_mode = True
