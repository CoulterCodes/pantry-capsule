from app.db import SessionLocal
from app.models import User, Preference

db = SessionLocal()

def seed():
    # Create a user
    user = User(
        email="test@example.com",
        name="Test User"
    )

# Create preferences linked to this user
    pref = Preference(
        user=user,
        eating_style="vegetarian",
        dirty_dozen_organic=True,
        brand_vs_cost="lowest_cost"
    )

    # Add both to the session
    db.add(user)
    db.add(pref)

    # Commit the transaction
    db.commit()

    print("Seed data inserted!")

if __name__ == "__main__":
    seed()