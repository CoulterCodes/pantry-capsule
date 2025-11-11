# init_db.py
from app.db import Base, engine
from app import models

# This will create all tables defined in your models.py
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")
