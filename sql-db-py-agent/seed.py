from models import User
from database import SessionLocal, engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

# Seed the database with initial data
def seed_database():
    session = SessionLocal()
    
    # Check if data already exists to avoid duplication
    if not session.query(User).first():
        # Add example users
        session.add(User(id=101, name="Alice", account_status="Active", subscription_plan="Pro Plan"))
        session.add(User(id=102, name="Bob", account_status="Locked", subscription_plan="Free Plan"))
        session.add(User(id=103, name="Charlie", account_status="Active", subscription_plan="Enterprise Plan"))
        session.commit()
        print("Database seeded successfully!")
    else:
        print("Database already seeded, skipping.")
    
    session.close()

# Run the seed function if this file is executed directly
if __name__ == "__main__":
    seed_database()