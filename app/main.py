"""Fitness Studio Booking API - Application Entry Point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.session import Base, engine
from app.modules.auth import auth_router
from app.modules.classes import classes_router
from app.modules.bookings import bookings_router

from app.core.logging import setup_logging

# Call the setup function right at the start
setup_logging()

logger = logging.getLogger(__name__)

# Create database tables
# The models get implicitly discovered by SQLAlchemy
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup...")
    yield
    logger.info("Application shutdown...")


app = FastAPI(
    title="Fitness Studio Booking API",
    description="API for booking fitness classes",
    version="0.1.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(auth_router, tags=["Authentication"])
app.include_router(classes_router, tags=["Classes"])
app.include_router(bookings_router, tags=["Bookings"])


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
