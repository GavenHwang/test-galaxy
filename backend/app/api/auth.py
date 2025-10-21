from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.models import User
from datetime import datetime
from app.api.common import get_user_by_name, create_access_token
from app.schemas.response import ResponseSchema

router = APIRouter()


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录接口
    - 接收用户名/密码
    - 验证凭证
    - 生成JWT Token
    """
    # 1. 从数据库获取用户
    user: User = await get_user_by_name(form_data.username)
    if not user:
        return ResponseSchema.error(code=401, msg="用户不存在")

    # 2. 验证密码
    is_authenticated = await user.authenticate(form_data.password)
    if not is_authenticated:
        return ResponseSchema.error(code=401, msg="用户名或密码错误")

    # 3. 更新最后登录时间
    user.last_login_time = datetime.now()
    await user.save()

    # 4. 生成 JWT Token
    token = create_access_token(user)

    return ResponseSchema.success(data={
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username
    })


@router.post("/logout", summary="登出接口")
async def logout():
    """
    登出接口,目前前端删除存储，后端先不做处理
    :return:
    """
    return ResponseSchema.success(data="")
