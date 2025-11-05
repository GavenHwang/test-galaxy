"""
UI测试用户管理API
"""
from fastapi import APIRouter, Query, Request
from typing import List, Optional
from datetime import datetime
from app.schemas.response import ResponseSchema
from app.schemas.ui_test import (
    TestUserCreateSchema,
    TestUserUpdateSchema,
    TestUserResponseSchema,
    TestUserListParams
)
from app.models.ui_test import TestCommonUser, TestUIElementPermission, TestUICasePermission, TestProductRole
from tortoise.expressions import Q

router = APIRouter()


def format_datetime(dt: datetime) -> str:
    """格式化时间为 YYYY-MM-DD HH:MM:SS 格式"""
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')


@router.post("", summary="创建测试用户", response_model=ResponseSchema[TestUserResponseSchema])
async def create_test_user(data: TestUserCreateSchema, request: Request):
    """
    创建测试用户
    
    业务规则：
    - 用户名在同一产品下唯一
    - 密码长度6-255位
    - 自动记录创建人
    """
    try:
        # 获取当前登录用户
        current_user = request.state.current_user
        created_by = current_user.get("username", "system") if current_user else "system"
        
        # 检查用户名是否在同一产品下已存在
        exists = await TestCommonUser.filter(
            username=data.username,
            product=data.product
        ).exists()
        
        if exists:
            return ResponseSchema.error(
                msg=f"用户名'{data.username}'在产品'{data.product}'下已存在",
                code=400
            )
        
        # 创建测试用户
        user = await TestCommonUser.create(
            username=data.username,
            password=data.password,
            product=data.product,
            role_name=data.role_name,
            description=data.description,
            created_by=created_by
        )
        
        # 构造响应数据（密码脱敏）
        user_data = TestUserResponseSchema(
            id=user.id,
            username=user.username,
            password="******",
            product=user.product,
            role_name=user.role_name,
            description=user.description,
            created_by=user.created_by,
            created_time=format_datetime(user.created_time),
            updated_time=format_datetime(user.updated_time)
        )
        
        return ResponseSchema.success(data=user_data, msg="创建成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("", summary="获取测试用户列表")
async def get_test_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    username: Optional[str] = Query(None, description="用户名模糊搜索"),
    product: Optional[str] = Query(None, description="产品名称精确匹配"),
    role_name: Optional[str] = Query(None, description="角色名称精确匹配")
):
    """
    分页获取测试用户列表
    
    支持筛选条件：
    - username: 用户名模糊搜索
    - product: 产品精确匹配
    - role_name: 角色精确匹配
    """
    try:
        # 构建查询条件
        query = TestCommonUser.all()
        
        if username:
            query = query.filter(username__icontains=username)
        if product:
            query = query.filter(product=product)
        if role_name:
            query = query.filter(role_name=role_name)
        
        # 查询总数
        total = await query.count()
        
        # 分页查询
        offset = (page - 1) * page_size
        users = await query.offset(offset).limit(page_size).order_by('-created_time')
        
        # 构造响应数据（密码脱敏）
        user_list = [
            TestUserResponseSchema(
                id=user.id,
                username=user.username,
                password="******",
                product=user.product,
                role_name=user.role_name,
                description=user.description,
                created_by=user.created_by,
                created_time=format_datetime(user.created_time),
                updated_time=format_datetime(user.updated_time)
            )
            for user in users
        ]
        
        # 构造分页响应
        result = {
            "items": user_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
        
        return ResponseSchema.success(data=result)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/{user_id}", summary="获取单个测试用户详情", response_model=ResponseSchema[TestUserResponseSchema])
async def get_test_user(user_id: int):
    """
    获取单个测试用户的详细信息
    """
    try:
        user = await TestCommonUser.get_or_none(id=user_id)
        
        if not user:
            return ResponseSchema.error(msg="测试用户不存在", code=404)
        
        # 构造响应数据（密码脱敏）
        user_data = TestUserResponseSchema(
            id=user.id,
            username=user.username,
            password="******",
            product=user.product,
            role_name=user.role_name,
            description=user.description,
            created_by=user.created_by,
            created_time=format_datetime(user.created_time),
            updated_time=format_datetime(user.updated_time)
        )
        
        return ResponseSchema.success(data=user_data)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.put("/{user_id}", summary="更新测试用户", response_model=ResponseSchema[TestUserResponseSchema])
async def update_test_user(user_id: int, data: TestUserUpdateSchema):
    """
    更新测试用户信息
    
    业务规则：
    - 支持部分字段更新
    - 如果提供密码则更新，否则保留原密码
    - 用户名修改时重新检查唯一性
    """
    try:
        user = await TestCommonUser.get_or_none(id=user_id)
        
        if not user:
            return ResponseSchema.error(msg="测试用户不存在", code=404)
        
        # 构建更新数据
        update_data = data.model_dump(exclude_unset=True)
        
        # 如果修改了用户名或产品，检查唯一性
        if 'username' in update_data or 'product' in update_data:
            new_username = update_data.get('username', user.username)
            new_product = update_data.get('product', user.product)
            
            # 排除自己检查是否存在重复
            exists = await TestCommonUser.filter(
                username=new_username,
                product=new_product
            ).exclude(id=user_id).exists()
            
            if exists:
                return ResponseSchema.error(
                    msg=f"用户名'{new_username}'在产品'{new_product}'下已存在",
                    code=400
                )
        
        # 更新字段
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await user.save()
        
        # 构造响应数据（密码脱敏）
        user_data = TestUserResponseSchema(
            id=user.id,
            username=user.username,
            password="******",
            product=user.product,
            role_name=user.role_name,
            description=user.description,
            created_by=user.created_by,
            created_time=format_datetime(user.created_time),
            updated_time=format_datetime(user.updated_time)
        )
        
        return ResponseSchema.success(data=user_data, msg="更新成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.delete("/{user_id}", summary="删除测试用户")
async def delete_test_user(user_id: int, force: bool = Query(False, description="强制删除（级联删除关联）")):
    """
    删除测试用户
    
    业务规则：
    - 检查是否有元素权限关联
    - 检查是否有用例权限关联
    - 如有关联且force=False，返回错误提示
    - 如force=True，级联删除关联记录
    """
    try:
        user = await TestCommonUser.get_or_none(id=user_id)
        
        if not user:
            return ResponseSchema.error(msg="测试用户不存在", code=404)
        
        # 检查关联
        element_perms_count = await TestUIElementPermission.filter(
            role_name=user.role_name
        ).count()
        
        case_perms_count = await TestUICasePermission.filter(
            role_name=user.role_name
        ).count()
        
        if (element_perms_count > 0 or case_perms_count > 0) and not force:
            return ResponseSchema.error(
                msg=f"该测试用户角色已关联{element_perms_count}个元素权限和{case_perms_count}个用例权限，请先解除关联或使用强制删除",
                code=400
            )
        
        # 如果强制删除，先删除关联记录
        if force:
            await TestUIElementPermission.filter(role_name=user.role_name).delete()
            await TestUICasePermission.filter(role_name=user.role_name).delete()
        
        # 删除用户
        await user.delete()
        
        return ResponseSchema.success(msg="删除成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/products/list", summary="获取产品列表")
async def get_products():
    """
    从产品角色字典表获取所有不重复的产品列表，用于下拉选择器
    """
    try:
        # 从字典表查询所有不重复的产品
        products = await TestProductRole.all().distinct().values_list('product', flat=True)
        
        # 过滤空值并排序
        products = sorted([p for p in products if p])
        
        return ResponseSchema.success(data=products)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/roles/list", summary="获取角色列表")
async def get_roles(product: Optional[str] = Query(None, description="产品名称，用于过滤角色")):
    """
    从产品角色字典表获取角色列表
    
    参数：
    - product: 可选，如果提供则只返回该产品下的角色
    """
    try:
        # 构建查询条件
        query = TestProductRole.all()
        
        if product:
            query = query.filter(product=product)
        
        # 查询所有不重复的角色
        roles = await query.distinct().values_list('role_name', flat=True)
        
        # 过滤空值并排序
        roles = sorted([r for r in roles if r])
        
        return ResponseSchema.success(data=roles)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)
