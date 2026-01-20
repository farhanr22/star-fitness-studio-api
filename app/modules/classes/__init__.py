"""Classes module exports."""

from .api import router as classes_router
from .service import get_class_by_id

__all__ = ["classes_router", "get_class_by_id"]