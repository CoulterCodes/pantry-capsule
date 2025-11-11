# app/core/config.py
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()  # reads .env in project root

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pantry.db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# split ALLOWED_ORIGINS into list
_allowed = os.getenv("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = [s.strip() for s in _allowed.split(",") if s.strip()]
