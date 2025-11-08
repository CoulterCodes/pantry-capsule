"""
Bootstrap script: run this from the project root (pantry-capsule) to create a working
FastAPI backend scaffold for PantryCapsule (vibe edition).

Usage (from project root):
  python pantrycapsule_backend_bootstrap.py

This will create `backend/app/...` files, requirements.txt, .env.example,
Dockerfile and docker-compose.yml. After running, follow the README steps printed.

Note: you should run this inside a virtualenv, and update .env with your real secrets.
"""
import os
from textwrap import dedent

ROOT = os.path.abspath(os.path.dirname(__file__))
BACKEND = os.path.join(ROOT, "backend")
APP = os.path.join(BACKEND, "app")
ROUTERS = os.path.join(APP, "routers")
UTILS = os.path.join(APP, "utils")

paths = [BACKEND, APP, ROUTERS, UTILS]
for p in paths:
    os.makedirs(p, exist_ok=True)

# __init__.py
open(os.path.join(APP, "__init__.py"), "w").close()
open(os.path.join(ROUTERS, "__init__.py"), "w").close()
open(os.path.join(UTILS, "__init__.py"), "w").close()

files = {
    os.path.join(APP, "db.py"): dedent('''
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker, declarative_base
        from dotenv import load_dotenv
        import os
        load_dotenv()
        DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql+psycopg2://postgres:postgres@localhost:5432/pantrycapsule"
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base = declarative_base()
    '''),

    os.path.join(APP, "models.py"): dedent('''
        from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
        from sqlalchemy.orm import relationship
        from app.db import Base

        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True, index=True)
            email = Column(String, unique=True, index=True, nullable=False)
            hashed_password = Column(String, nullable=False)
            is_active = Column(Boolean, default=True)
            preferences = relationship("Preference", back_populates="owner")

        class Preference(Base):
            __tablename__ = "preferences"
            id = Column(Integer, primary_key=True, index=True)
            name = Column(String, nullable=False)
            value = Column(String, nullable=False)
            owner_id = Column(Integer, ForeignKey("users.id"))
            owner = relationship("User", back_populates="preferences")
    '''),

    os.path.join(APP, "schemas.py"): dedent('''
        from pydantic import BaseModel
        from typing import List, Optional

        class PreferenceBase(BaseModel):
            name: str
            value: str

        class PreferenceCreate(PreferenceBase):
            pass

        class Preference(PreferenceBase):
            id: int
            owner_id: int
            class Config:
                orm_mode = True

        class UserBase(BaseModel):
            email: str

        class UserCreate(UserBase):
            password: str

        class User(UserBase):
            id: int
            is_active: bool
            preferences: List[Preference] = []
            class Config:
                orm_mode = True
    '''),

    os.path.join(APP, "crud.py"): dedent('''
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
    '''),

    os.path.join(APP, "utils", "security.py"): dedent('''
        from passlib.context import CryptContext
        from datetime import datetime, timedelta
        from jose import jwt
        import os
        from dotenv import load_dotenv
        load_dotenv()
        SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")
        ALGORITHM = os.getenv("ALGORITHM", "HS256")
        ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        def hash_password(password: str) -> str:
            return pwd_context.hash(password)

        def verify_password(plain: str, hashed: str) -> bool:
            return pwd_context.verify(plain, hashed)

        def create_access_token(data: dict):
            to_encode = data.copy()
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            to_encode.update({"exp": expire})
            return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        def decode_token(token: str):
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    '''),

    os.path.join(APP, "routers", "auth.py"): dedent('''
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
    '''),

    os.path.join(APP, "routers", "users.py"): dedent('''
        from fastapi import APIRouter, Depends, HTTPException
        from sqlalchemy.orm import Session
        from app.db import SessionLocal
        from app import crud, schemas

        router = APIRouter(prefix="/users", tags=["users"])

        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()

        @router.get("/", response_model=list[schemas.User])
        def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
            return crud.get_users(db, skip=skip, limit=limit)
    '''),

    os.path.join(APP, "routers", "preferences.py"): dedent('''
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
    '''),

    os.path.join(APP, "main.py"): dedent('''
        from fastapi import FastAPI
        from app.db import Base, engine
        from app.routers import auth, users, preferences

        # create DB tables (for dev; use alembic in prod)
        Base.metadata.create_all(bind=engine)

        app = FastAPI(title='PantryCapsule Vibe Backend')

        app.include_router(auth.router)
        app.include_router(users.router)
        app.include_router(preferences.router)

        @app.get('/')
        def root():
            return {'message': 'PantryCapsule Vibe Backend is live'}
    '''),

    os.path.join(BACKEND, "requirements.txt"): dedent('''
        fastapi
        uvicorn[standard]
        sqlalchemy
        psycopg2-binary
        python-dotenv
        passlib[bcrypt]
        python-jose[cryptography]
        pydantic
    '''),

    os.path.join(BACKEND, ".env.example"): dedent('''
        DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/pantrycapsule
        SECRET_KEY=change_me_to_a_random_secret
        ALGORITHM=HS256
        ACCESS_TOKEN_EXPIRE_MINUTES=60
    '''),

    os.path.join(ROOT, "docker-compose.yml"): dedent('''
        version: '3.9'
        services:
          db:
            image: postgres:15
            restart: always
            environment:
              POSTGRES_USER: postgres
              POSTGRES_PASSWORD: postgres
              POSTGRES_DB: pantrycapsule
            ports:
              - '5432:5432'
            volumes:
              - postgres_data:/var/lib/postgresql/data
          backend:
            build: ./backend
            command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
            volumes:
              - ./backend:/code
            ports:
              - '8000:8000'
            depends_on:
              - db
        volumes:
          postgres_data:
    '''),

    os.path.join(BACKEND, "Dockerfile"): dedent('''
        FROM python:3.11-slim
        WORKDIR /code
        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt
        COPY ./app ./app
        CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    '''),

    os.path.join(BACKEND, "README.md"): dedent('''
        # PantryCapsule Backend (Vibe)
        
        ## Quickstart (dev)
        
        - Create a Python venv and activate it
        - Install dependencies: `pip install -r requirements.txt`
        - Copy `.env.example` to `.env` and edit
        - Run the app: `uvicorn app.main:app --reload`
    '''),
}

# Write files
for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Scaffold created under ./backend. Next steps:\n")
print("1) cd backend")
print("2) python -m venv venv")
print("3) .\\venv\\Scripts\\activate    # Windows")
print("4) pip install -r requirements.txt")
print("5) copy .env.example .env and edit DATABASE_URL/SECRET_KEY")
print("6) uvicorn app.main:app --reload")
print("\nWhen ready we can add Alembic migrations, seeders, and CI/CD.")
