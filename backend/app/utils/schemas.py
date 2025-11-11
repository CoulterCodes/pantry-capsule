# add these to your pydantic schemas file
from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class UserCreate(BaseModel):
    email: str
    password: str
    username: Optional[str] = None

class LoginSchema(BaseModel):
    identifier: str  # email or username
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
