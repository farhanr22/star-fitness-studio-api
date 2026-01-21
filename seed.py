"""
Script for seeding the database with initial data for testing.
- Clears the existing database
- Creates 2 new users, 6 classes and 2 bookings
- Provides email and password to enable login and further API testing
"""

import logging
from datetime import datetime, timedelta, timezone

from app.db.session import SessionLocal, engine, Base
from app.modules.auth.service import create_user
from app.modules.classes.service import create_class
from app.modules.bookings.service import create_booking
from app.modules.classes.schemas import ClassCreate
from app.modules.bookings.schemas import BookingCreate

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create a new database session
db = SessionLocal()


def seed_data():
    """
    Seeds the database with users, classes, and bookings.
    """

    logger.info("Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)

    logger.info("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    # Seed Users

    logger.info("Seeding users...")
    user_data = [
        {
            "name": "First User",
            "email": "first.user@example.com",
            "password": "password123",
        },
        {
            "name": "Second User",
            "email": "second.user@example.com",
            "password": "password456",
        },
    ]

    users = [
        create_user(db, name=u["name"], email=u["email"], password=u["password"])
        for u in user_data
    ]
    for user in users:
        logger.info(f"Created user: {user.name} (ID: {user.id})")

    first_user, second_user = users

    # Seed Classes

    logger.info("Seeding classes...")
    class_types = ["Exercise", "Stretching"]
    created_classes = []

    for user in users:
        first_name = user.name.split()[0]
        for i, class_type in enumerate(class_types):
            class_schema = ClassCreate(
                name=f"{first_name}'s {class_type} Class",
                instructor=user.name,
                dateTime=datetime.now(timezone.utc) + timedelta(days=i + 1, hours=i),
                availableSlots=10 + i,
            )
            new_class = create_class(db, class_data=class_schema, creator_id=user.id)
            created_classes.append(new_class)

    # Seed Bookings
    logger.info("Seeding bookings...")

    # First user books one of Second user's classes
    second_user_class = next(
        c for c in created_classes if c.creator_id == second_user.id
    )
    booking_schema_1 = BookingCreate(
        class_id=second_user_class.id,
        client_name=first_user.name,
        client_email=first_user.email,
    )
    booking1 = create_booking(db, user=first_user, booking_data=booking_schema_1)

    # Second user books one of First user's classes
    first_user_class = next(c for c in created_classes if c.creator_id == first_user.id)
    booking_schema_2 = BookingCreate(
        class_id=first_user_class.id,
        client_name=second_user.name,
        client_email=second_user.email,
    )
    booking2 = create_booking(db, user=second_user, booking_data=booking_schema_2)

    # Print Login Details
    print("\n" + "=" * 50)
    print("✅ Seeding complete!")
    print("\nUse these credentials to log in and test the API:")
    print(f"👤 Email:    {user_data[0]['email']}")
    print(f"🔑 Password: {user_data[0]['password']}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    try:
        seed_data()
    except Exception as e:
        logger.error("An error occurred during seeding:", exc_info=True)
    finally:
        db.close()
