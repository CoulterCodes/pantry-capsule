# app/core/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
from app.core.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

# password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    pw = password if isinstance(password, str) else str(password)
    # bcrypt truncates at 72 bytes; truncate here to avoid backend errors
    if len(pw.encode("utf-8")) > 72:
        pw = pw[:72]
    return pwd_context.hash(pw)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pw = plain_password if isinstance(plain_password, str) else str(plain_password)
    if len(pw.encode("utf-8")) > 72:
        pw = pw[:72]
    return pwd_context.verify(pw, hashed_password)

# JWT
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=(expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def _decode_token(token: str) -> Optional[dict]:
    """Return payload dict or None if invalid/expired."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# oauth2 scheme for dependency injection in routers
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# helper used by routers to validate token and return user id (or raise)
from fastapi import HTTPException, status

def verify_access_token(token: str, credentials_exception: HTTPException):
    """
    Validate token and return user id (int). If invalid, raise the provided credentials_exception.
    This matches the pattern used in routers/get_current_user.
    """
    payload = _decode_token(token)
    if payload is None or "sub" not in payload:
        raise credentials_exception
    try:
        return int(payload["sub"])
    except Exception:
        raise credentials_exception
