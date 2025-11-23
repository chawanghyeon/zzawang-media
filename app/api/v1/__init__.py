from fastapi import APIRouter

from .dashboard import router as dashboard_router
from .feedback import router as feedback_router
from .script import router as script_router
from .submit import router as submit_router

api_router = APIRouter()

api_router.include_router(script_router)
api_router.include_router(submit_router)
api_router.include_router(feedback_router)
api_router.include_router(dashboard_router)

__all__ = ["api_router"]
