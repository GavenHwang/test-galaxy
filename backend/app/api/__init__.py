from fastapi import APIRouter
from .auth import router as auth_router
from .user import router as user_router
from .env import router as env_router
from .product import router as product_router
from .ui_test_user import router as ui_test_user_router
from .ui_element import router as ui_element_router
from .ui_test_case import router as ui_test_case_router
from .ui_test_suite import router as ui_test_suite_router
from .ui_test_task import router as ui_test_task_router
from .ui_test_report import router as ui_test_report_router
from .menu_permission import router as menu_permission_router

api_router = APIRouter()
api_router.include_router(auth_router, tags=["认证模块"])
api_router.include_router(user_router, prefix="/user", tags=["用户模块"])
api_router.include_router(env_router, prefix="/env", tags=["环境模块"])
api_router.include_router(product_router, prefix="/products", tags=["产品管理"])
api_router.include_router(ui_test_user_router, prefix="/ui-test/test-users", tags=["UI测试-测试用户"])
api_router.include_router(ui_element_router, prefix="/ui-test/elements", tags=["UI测试-页面元素"])
api_router.include_router(ui_test_case_router, prefix="/ui-test/test-cases", tags=["UI测试-测试用例"])
api_router.include_router(ui_test_suite_router, prefix="/ui-test/test-suites", tags=["UI测试-测试套件"])
api_router.include_router(ui_test_task_router, prefix="/ui-test/test-tasks", tags=["UI测试-测试单"])
api_router.include_router(ui_test_report_router, prefix="/ui-test/test-reports", tags=["UI测试-测试报告"])
api_router.include_router(menu_permission_router, prefix="/menu-permissions", tags=["菜单权限管理"])

__all__ = ["api_router"]

