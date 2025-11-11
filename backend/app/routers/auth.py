# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import User
from app.core import security
from app.utils import schemas

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # allow registering with email and optional username
    exists = db.query(User).filter((User.email == user.email) | (User.username == getattr(user, "username", None))).first()
    if exists:
        raise HTTPException(status_code=400, detail="User with that email or username already exists")
    hashed = security.hash_password(user.password)
    db_user = User(email=user.email, username=getattr(user, "username", None), password=hashed, is_active=True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.LoginSchema, db: Session = Depends(get_db)):
    # accept email OR username
    ident = credentials.identifier
    user = db.query(User).filter((User.email == ident) | (User.username == ident)).first()
    if not user or not security.verify_password(credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = security.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
