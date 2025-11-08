
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.db import SessionLocal
from app.utils.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post('/signup', response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail='Email already registered')
    return crud.create_user(db, user)

@router.post('/token')
def login(form_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.email)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail='Incorrect credentials')
    token = create_access_token({"sub": user.email, "user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}
