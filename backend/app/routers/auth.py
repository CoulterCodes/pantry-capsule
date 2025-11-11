# backend/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, utils
from app.db import SessionLocal
from app.models import User
from app.core import security
from app.utils import schemas

router = APIRouter(prefix="/auth", tags=["auth"])

# Dependency to get DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------
# Register new user
# ----------------------------

@router.post("/register", status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        (models.User.email == user.email) | (models.User.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = utils.hash_password(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully"}

# ----------------------------
# Login user
# ----------------------------
@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    # Look up by email or username
    db_user = None
    if user.email:
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
    elif user.username:
        db_user = db.query(models.User).filter(models.User.username == user.username).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username or password."
        )

    if not utils.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username or password."
        )

    access_token = utils.create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
