"""Fitness Studio Booking API - Application Entry Point."""

from fastapi import FastAPI

app = FastAPI(
    title="Fitness Studio Booking API",
    description="API for booking fitness classes",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
