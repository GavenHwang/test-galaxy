from fastapi import APIRouter
from .auth import router as auth_router
from .user import router as user_router
from .env import router as env_router

api_router = APIRouter()
api_router.include_router(auth_router, tags=["认证模块"])
api_router.include_router(user_router, prefix="/user", tags=["用户模块"])
api_router.include_router(env_router, prefix="/env", tags=["环境模块"])

__all__ = ["api_router"]

