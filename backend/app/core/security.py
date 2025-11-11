# app/core/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
from app.core.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Password helpers
def hash_password(password: str) -> str:
    # bcrypt truncates at 72 bytes — best practice: reject overly long raw password in frontend OR shorten here
    pw = password if isinstance(password, str) else str(password)
    if len(pw.encode("utf-8")) > 72:
        pw = pw[:72]
    return pwd_context.hash(pw)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pw = plain_password if isinstance(plain_password, str) else str(plain_password)
    if len(pw.encode("utf-8")) > 72:
        pw = pw[:72]
    return pwd_context.verify(pw, hashed_password)

# JWT helpers
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_minutes: Optional[int] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=(expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
