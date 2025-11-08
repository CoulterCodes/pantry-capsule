from fastapi import FastAPI
from app.routers import meal_planner

app = FastAPI()

app.include_router(meal_planner.router)

@app.get("/")
def root():
    return {"message": "Pantry Capsule API is running!"}