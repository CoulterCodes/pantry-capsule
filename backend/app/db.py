from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --- Database connection ---
DATABASE_URL = "postgresql+psycopg2://postgres:dSean$ter531!@localhost:5432/pantrycapsule"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Base class for models ---
Base = declarative_base()

# --- Create tables if this file is run directly ---
if __name__ == "__main__":
    print("Base id in db:", id(Base))
    print("Tables registered so far:", Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)
    print("Tables created:", Base.metadata.tables.keys())
