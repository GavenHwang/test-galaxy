"""
创建APP对象，初始化框架
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from tortoise import Tortoise
from app.api import api_router
from fastapi.openapi.utils import get_openapi
from app.core.init_app import register_scheduled_jobs, start_scheduler, shutdown_scheduler

from app.core.init_app import (
    init_data,
    make_middlewares,
)

try:
    from app.settings.config import settings
except ImportError:
    raise AssertionError("Can not import settings")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_data()
    register_routers(app)
    # 注册定时任务
    register_scheduled_jobs()
    # 启动定时任务调度器
    await start_scheduler()
    yield
    # 关闭定时任务
    await shutdown_scheduler()
    await Tortoise.close_connections()


def register_routers(app):
    """注册路由"""
    app.include_router(api_router, prefix="/api")


def create_app() -> FastAPI:
    """创建app"""
    app = FastAPI(
        title=settings.APP_TITLE,
        description=settings.APP_DESCRIPTION,
        version=settings.VERSION,
        openapi_url="/openapi.json",
        middleware=make_middlewares(),
        lifespan=lifespan,
    )

    # 正确扩展OpenAPI模式（保留路由信息）
    def custom_openapi():
        # 1. 先获取自动生成的OpenAPI模式（包含所有扫描到的模型）
        openapi_schema = get_openapi(
            title=settings.APP_TITLE,
            version=settings.VERSION,
            description=settings.APP_DESCRIPTION,
            routes=app.routes,
        )

        # 2. 添加安全方案（不要覆盖整个模式）
        openapi_schema["security"] = [{"BearerAuth": []}]
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
        return openapi_schema

        # 替换默认的openapi生成函数

    app.openapi = custom_openapi
    # register_exceptions(app)
    return app


app = create_app()
