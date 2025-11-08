
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app import crud, schemas

router = APIRouter(prefix="/preferences", tags=["preferences"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post('/users/{user_id}', response_model=schemas.Preference)
def add_pref(user_id: int, pref: schemas.PreferenceCreate, db: Session = Depends(get_db)):
    return crud.create_preference(db, user_id, pref)

@router.get('/', response_model=list[schemas.Preference])
def list_prefs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_preferences(db, skip=skip, limit=limit)
