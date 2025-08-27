# app/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import User, Preference

app = FastAPI(title="PantryCapsule API")

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Welcome to PantryCapsule API!"}

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(Preference).all()