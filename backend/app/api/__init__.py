from fastapi import APIRouter
from .auth import router as auth_router
from .user import router as user_router
from .env import router as env_router
from .ui_test_user import router as ui_test_user_router
from .ui_element import router as ui_element_router

api_router = APIRouter()
api_router.include_router(auth_router, tags=["认证模块"])
api_router.include_router(user_router, prefix="/user", tags=["用户模块"])
api_router.include_router(env_router, prefix="/env", tags=["环境模块"])
api_router.include_router(ui_test_user_router, prefix="/ui-test/test-users", tags=["UI测试-测试用户"])
api_router.include_router(ui_element_router, prefix="/ui-test/elements", tags=["UI测试-页面元素"])

__all__ = ["api_router"]

