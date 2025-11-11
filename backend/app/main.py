from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import meal_planner, auth

app = FastAPI()

app.include_router(meal_planner.router)
app.include_router(auth.router)

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Pantry Capsule API is running!"}
