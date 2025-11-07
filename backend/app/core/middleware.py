from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from app.models.user import User  # 假设 User 模型在这里
from app.settings import settings  # 从 settings 导入密钥和算法
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    @staticmethod
    async def get_user_by_id(user_id: str):
        # 这里应该是数据库查询逻辑，返回用户对象或 None
        # 示例代码，实际需要替换为数据库查询
        user = await User.get(id=user_id).select_related("role")
        return user

    async def dispatch(self, request: Request, call_next):

        if request.method == "OPTIONS":
            return await call_next(request)
        # 中间件逻辑，同上
        # 跳过某些不需要鉴权的路径，例如登录接口
        if request.url.path in ["/api/logout", "/api/token", "/api/login", "/docs", "/openapi.json"]:
            return await call_next(request)

        # 从请求头中获取 Authorization
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(content={"code": 401, "msg": "Token missing or invalid format"}, status_code=401)

        token = auth_header.split()[1]

        try:
            # 验证 Token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            # 校验
            user_id = payload.get("sub")
            if not user_id:
                return JSONResponse(content={"code": 401, "msg": "Invalid token - user ID missing"}, status_code=401)

            # 模拟从数据库获取用户
            user = await self.get_user_by_id(user_id)
            if not user:
                return JSONResponse(content={"code": 401, "msg": "Invalid token - user not found"}, status_code=401)

            # 将用户信息存入 request.state，供后续视图函数使用
            request.state.current_user = {
                "id": user.id, 
                "username": user.username,  # 修改为 username，与 API 中的获取方式一致
                "role": user.role.name if user.role else None
            }

        except JWTError as e:
            return JSONResponse(content={"code": 401, "msg": "Invalid token"}, status_code=401)

        response = await call_next(request)
        return response