"""Fitness Studio Booking API - Application Entry Point."""

from fastapi import FastAPI

from app.db.session import Base, engine
from app.modules.auth import auth_router
from app.modules.classes import classes_router
from app.modules.bookings   import bookings_router

# Create database tables
# The models get implicitly discovered by SQLAlchemy
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fitness Studio Booking API",
    description="API for booking fitness classes",
    version="0.1.0",
)

# Include routers
app.include_router(auth_router, tags=["Authentication"])
app.include_router(classes_router, tags=["Classes"])
app.include_router(bookings_router, tags=["Bookings"])


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
