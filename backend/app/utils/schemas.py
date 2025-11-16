from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

# -----------------------------
# Authentication
# -----------------------------
class UserCreate(BaseModel):
    email: str
    password: str
    username: Optional[str] = None


class LoginSchema(BaseModel):
    identifier: str  # email or username
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# -----------------------------
# FoodItem
# -----------------------------
class FoodItemBase(BaseModel):
    name: str
    category: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    tags: Optional[str] = None
    source: Optional[str] = None


class FoodItemRead(FoodItemBase):
    id: int

    class Config:
        from_attributes = True


# -----------------------------
# Recipe
# -----------------------------
class RecipeBase(BaseModel):
    name: str
    servings: Optional[float] = None
    instructions: Optional[str] = None
    source_url: Optional[str] = None
    tags: Optional[str] = None


class RecipeRead(RecipeBase):
    id: int
    ingredients: List[FoodItemRead] = Field(default_factory=list)

    class Config:
        from_attributes = True


# -----------------------------
# Meal
# -----------------------------
class MealBase(BaseModel):
    name: str
    meal_type: Optional[str] = None


class MealRead(MealBase):
    id: int
    food_items: List[FoodItemRead] = Field(default_factory=list)
    recipes: List[RecipeRead] = Field(default_factory=list)

    class Config:
        from_attributes = True


# -----------------------------
# MealPlan
# -----------------------------
class MealPlanBase(BaseModel):
    date: date


class MealPlanRead(MealPlanBase):
    id: int
    meals: List[MealRead] = Field(default_factory=list)

    class Config:
        from_attributes = True


# -----------------------------
# Preferences & Restrictions
# -----------------------------
class PreferenceBase(BaseModel):
    key: str
    value: str


class PreferenceRead(PreferenceBase):
    id: int

    class Config:
        from_attributes = True


class RestrictionBase(BaseModel):
    food_item_id: int


class RestrictionRead(RestrictionBase):
    id: int

    class Config:
        from_attributes = True


# -----------------------------
# User
# -----------------------------
class UserBase(BaseModel):
    username: str
    email: str


class UserRead(UserBase):
    id: int
    is_active: bool
    preferences: List[PreferenceRead] = Field(default_factory=list)
    restrictions: List[RestrictionRead] = Field(default_factory=list)

    class Config:
        from_attributes = True


# Backward compatibility aliases for existing routers
User = UserRead
MealPlanOut = MealPlanRead
MealOut = MealRead
FoodItemOut = FoodItemRead
