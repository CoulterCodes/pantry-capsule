from sqlalchemy import Column, Integer, String, ForeignKey, Table, Float, Boolean, Date
from sqlalchemy.orm import relationship
from .db import Base

# -----------------------------
# Association Tables
# -----------------------------

# Many-to-many between Meals and FoodItems
meal_food_association = Table(
    "meal_foods",
    Base.metadata,
    Column("meal_id", Integer, ForeignKey("meals.id")),
    Column("food_item_id", Integer, ForeignKey("food_items.id")),
)

# Many-to-many between MealPlans and Meals
mealplan_meals_association = Table(
    "mealplan_meals",
    Base.metadata,
    Column("mealplan_id", Integer, ForeignKey("meal_plans.id")),
    Column("meal_id", Integer, ForeignKey("meals.id")),
)

# -----------------------------
# User and Preferences
# -----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)

    preferences = relationship("Preference", back_populates="user", cascade="all, delete")
    meal_plans = relationship("MealPlan", back_populates="user")
    food_history = relationship("UserFoodHistory", back_populates="user")
    restrictions = relationship("Restriction", back_populates="user")


class Preference(Base):
    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    key = Column(String, index=True)
    value = Column(String)

    user = relationship("User", back_populates="preferences")


# -----------------------------
# FoodItem
# -----------------------------
class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String, index=True)
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    tags = Column(String)  # comma-separated tags

# -----------------------------
# Meal
# -----------------------------
class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    meal_type = Column(String, index=True)  # breakfast, lunch, dinner, snack
    food_items = relationship("FoodItem", secondary=meal_food_association, backref="meals")
    meal_plans = relationship("MealPlan", secondary=mealplan_meals_association, back_populates="meals")

# -----------------------------
# MealPlan
# -----------------------------
class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date)

    user = relationship("User", back_populates="meal_plans")
    meals = relationship("Meal", secondary=mealplan_meals_association, back_populates="meal_plans")

# -----------------------------
# User Food History
# -----------------------------
class UserFoodHistory(Base):
    __tablename__ = "user_food_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_item_id = Column(Integer, ForeignKey("food_items.id"))
    removed_count = Column(Integer, default=0)
    liked = Column(Boolean, default=True)

    user = relationship("User", back_populates="food_history")

# -----------------------------
# Restrictions
# -----------------------------
class Restriction(Base):
    __tablename__ = "restrictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_item_id = Column(Integer, ForeignKey("food_items.id"))

    user = relationship("User", back_populates="restrictions")
