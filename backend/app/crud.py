
from sqlalchemy.orm import Session
from app import models, schemas
from app.utils.security import hash_password

# Users
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed = hash_password(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

# Preferences
def create_preference(db: Session, user_id: int, pref: schemas.PreferenceCreate):
    db_pref = models.Preference(name=pref.name, value=pref.value, owner_id=user_id)
    db.add(db_pref)
    db.commit()
    db.refresh(db_pref)
    return db_pref

def get_preferences(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Preference).offset(skip).limit(limit).all()
