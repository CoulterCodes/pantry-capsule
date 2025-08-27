from .db import Base, engine
from . import models
print("Base id in init_db:", id(Base))
Base.metadata.create_all(bind=engine)
print("Tables created:", Base.metadata.tables.keys())