
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
