from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class User(Base):
    __tablename__ = "users" # The name of the table in Postgres

    id = Column(Integer, primary_key=True, index=True) # unique row ID
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)

    # link to preferences
    preferences = relationship("Preference", back_populates="user")

class Preference(Base):
    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # link back to users
    eating_style = Column(String)
    dirty_dozen_organic = Column(Boolean, default=False)
    brand_vs_cost = Column(String) # "brand" or "lowest_cost"

    user = relationship("User", back_populates="preferences")

print("Models.py executed!")
print("Base id in models:", id(Base))