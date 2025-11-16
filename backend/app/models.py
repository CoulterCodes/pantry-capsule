from sqlalchemy import Column, Integer, String, ForeignKey, Table, Float, Boolean, Date, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

# -----------------------------
# User and Preferences
# -----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

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
# Association Tables
# -----------------------------
meal_food_association = Table(
    "meal_foods",
    Base.metadata,
    Column("meal_id", Integer, ForeignKey("meals.id")),
    Column("food_item_id", Integer, ForeignKey("food_items.id")),
)

mealplan_meals_association = Table(
    "mealplan_meals",
    Base.metadata,
    Column("mealplan_id", Integer, ForeignKey("meal_plans.id")),
    Column("meal_id", Integer, ForeignKey("meals.id")),
)

meal_recipe_association = Table(
    "meal_recipes",
    Base.metadata,
    Column("meal_id", Integer, ForeignKey("meals.id")),
    Column("recipe_id", Integer, ForeignKey("recipes.id")),
)

# -----------------------------
# FoodItem
# -----------------------------
class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    tags = Column(String)
    source = Column(String)

    category = relationship("Category", back_populates="items")
    recipe_ingredients = relationship("RecipeIngredient", back_populates="food_item", lazy="selectin")

# -----------------------------
# Category
# -----------------------------
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    items = relationship("FoodItem", back_populates="category", lazy="selectin")

# -----------------------------
# Recipe
# -----------------------------
class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    servings = Column(Float)
    instructions = Column(String)
    source_url = Column(String, nullable=True)
    tags = Column(String)

    ingredients = relationship("RecipeIngredient", back_populates="recipe", lazy="selectin")

# -----------------------------
# RecipeIngredient
# -----------------------------
class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    food_item_id = Column(Integer, ForeignKey("food_items.id"))
    quantity = Column(Float, nullable=True)

    recipe = relationship("Recipe", back_populates="ingredients")
    food_item = relationship("FoodItem", back_populates="recipe_ingredients")

# -----------------------------
# Meal
# -----------------------------
class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    meal_type = Column(String, index=True)

    food_items = relationship("FoodItem", secondary=meal_food_association, backref="meals")
    recipes = relationship("Recipe", secondary=meal_recipe_association, backref="meals")
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
# UserFoodHistory
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
# Restriction
# -----------------------------
class Restriction(Base):
    __tablename__ = "restrictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_item_id = Column(Integer, ForeignKey("food_items.id"))

    user = relationship("User", back_populates="restrictions")

# -----------------------------
# ProduceClassification
# -----------------------------
class ProduceClassification(Base):
    __tablename__ = "produce_classifications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    year = Column(Integer, index=True)
    produce_items = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)

    def get_items(self):
        return [item.strip() for item in self.produce_items.split(",") if item.strip()]
