"""
产品角色字典管理API
"""
from fastapi import APIRouter, Query, Request
from typing import Optional
from datetime import datetime
from app.schemas.response import ResponseSchema
from pydantic import BaseModel, Field
from app.models.ui_test import TestProductRole

router = APIRouter()


def format_datetime(dt: datetime) -> str:
    """格式化时间为 YYYY-MM-DD HH:MM:SS 格式"""
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')


# ==================== Schema 定义 ====================

class ProductRoleCreateSchema(BaseModel):
    """创建产品角色请求"""
    product: str = Field(..., min_length=1, max_length=100, description="产品名称")
    role_name: str = Field(..., min_length=1, max_length=100, description="角色名称")
    role_code: str = Field(..., min_length=1, max_length=50, description="角色编码")
    description: Optional[str] = Field(None, max_length=500, description="描述")


class ProductRoleUpdateSchema(BaseModel):
    """更新产品角色请求"""
    product: Optional[str] = Field(None, min_length=1, max_length=100, description="产品名称")
    role_name: Optional[str] = Field(None, min_length=1, max_length=100, description="角色名称")
    role_code: Optional[str] = Field(None, min_length=1, max_length=50, description="角色编码")
    description: Optional[str] = Field(None, max_length=500, description="描述")


class ProductRoleResponseSchema(BaseModel):
    """产品角色响应"""
    id: int
    product: str
    role_name: str
    role_code: str
    description: Optional[str] = None
    created_by: str
    created_time: str
    updated_time: str

    class Config:
        from_attributes = True


# ==================== API 路由 ====================

@router.post("", summary="创建产品角色", response_model=ResponseSchema[ProductRoleResponseSchema])
async def create_product_role(data: ProductRoleCreateSchema, request: Request):
    """
    创建产品角色
    
    业务规则：
    - 产品和角色组合唯一
    - 自动记录创建人
    """
    try:
        # 获取当前登录用户
        current_user = request.state.current_user
        created_by = current_user.get("username", "system") if current_user else "system"
        
        # 检查产品角色组合是否已存在
        exists = await TestProductRole.filter(
            product=data.product,
            role_name=data.role_name
        ).exists()
        
        if exists:
            return ResponseSchema.error(
                msg=f"产品'{data.product}'下角色'{data.role_name}'已存在",
                code=400
            )
        
        # 创建产品角色
        product_role = await TestProductRole.create(
            product=data.product,
            role_name=data.role_name,
            role_code=data.role_code,
            description=data.description,
            created_by=created_by
        )
        
        # 构造响应数据
        result = ProductRoleResponseSchema(
            id=product_role.id,
            product=product_role.product,
            role_name=product_role.role_name,
            role_code=product_role.role_code,
            description=product_role.description,
            created_by=product_role.created_by,
            created_time=format_datetime(product_role.created_time),
            updated_time=format_datetime(product_role.updated_time)
        )
        
        return ResponseSchema.success(data=result, msg="创建成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("", summary="获取产品角色列表")
async def get_product_roles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    product: Optional[str] = Query(None, description="产品名称精确匹配"),
    role_name: Optional[str] = Query(None, description="角色名称模糊搜索")
):
    """
    分页获取产品角色列表
    
    支持筛选条件：
    - product: 产品精确匹配
    - role_name: 角色名称模糊搜索
    """
    try:
        # 构建查询条件
        query = TestProductRole.all()
        
        if product:
            query = query.filter(product=product)
        if role_name:
            query = query.filter(role_name__icontains=role_name)
        
        # 查询总数
        total = await query.count()
        
        # 分页查询
        offset = (page - 1) * page_size
        product_roles = await query.offset(offset).limit(page_size).order_by('-created_time')
        
        # 构造响应数据
        result_list = [
            ProductRoleResponseSchema(
                id=pr.id,
                product=pr.product,
                role_name=pr.role_name,
                role_code=pr.role_code,
                description=pr.description,
                created_by=pr.created_by,
                created_time=format_datetime(pr.created_time),
                updated_time=format_datetime(pr.updated_time)
            )
            for pr in product_roles
        ]
        
        # 构造分页响应
        result = {
            "items": result_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
        
        return ResponseSchema.success(data=result)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/{product_role_id}", summary="获取单个产品角色详情", response_model=ResponseSchema[ProductRoleResponseSchema])
async def get_product_role(product_role_id: int):
    """
    获取单个产品角色的详细信息
    """
    try:
        product_role = await TestProductRole.get_or_none(id=product_role_id)
        
        if not product_role:
            return ResponseSchema.error(msg="产品角色不存在", code=404)
        
        # 构造响应数据
        result = ProductRoleResponseSchema(
            id=product_role.id,
            product=product_role.product,
            role_name=product_role.role_name,
            role_code=product_role.role_code,
            description=product_role.description,
            created_by=product_role.created_by,
            created_time=format_datetime(product_role.created_time),
            updated_time=format_datetime(product_role.updated_time)
        )
        
        return ResponseSchema.success(data=result)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.put("/{product_role_id}", summary="更新产品角色", response_model=ResponseSchema[ProductRoleResponseSchema])
async def update_product_role(product_role_id: int, data: ProductRoleUpdateSchema):
    """
    更新产品角色信息
    
    业务规则：
    - 支持部分字段更新
    - 修改产品或角色时重新检查唯一性
    """
    try:
        product_role = await TestProductRole.get_or_none(id=product_role_id)
        
        if not product_role:
            return ResponseSchema.error(msg="产品角色不存在", code=404)
        
        # 构建更新数据
        update_data = data.model_dump(exclude_unset=True)
        
        # 如果修改了产品或角色，检查唯一性
        if 'product' in update_data or 'role_name' in update_data:
            new_product = update_data.get('product', product_role.product)
            new_role_name = update_data.get('role_name', product_role.role_name)
            
            # 排除自己检查是否存在重复
            exists = await TestProductRole.filter(
                product=new_product,
                role_name=new_role_name
            ).exclude(id=product_role_id).exists()
            
            if exists:
                return ResponseSchema.error(
                    msg=f"产品'{new_product}'下角色'{new_role_name}'已存在",
                    code=400
                )
        
        # 更新字段
        for field, value in update_data.items():
            setattr(product_role, field, value)
        
        await product_role.save()
        
        # 构造响应数据
        result = ProductRoleResponseSchema(
            id=product_role.id,
            product=product_role.product,
            role_name=product_role.role_name,
            role_code=product_role.role_code,
            description=product_role.description,
            created_by=product_role.created_by,
            created_time=format_datetime(product_role.created_time),
            updated_time=format_datetime(product_role.updated_time)
        )
        
        return ResponseSchema.success(data=result, msg="更新成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.delete("/{product_role_id}", summary="删除产品角色")
async def delete_product_role(product_role_id: int):
    """
    删除产品角色
    
    业务规则：
    - 检查是否有测试用户使用该产品角色组合
    - 如有使用，返回错误提示
    """
    try:
        product_role = await TestProductRole.get_or_none(id=product_role_id)
        
        if not product_role:
            return ResponseSchema.error(msg="产品角色不存在", code=404)
        
        # 检查是否有测试用户使用该产品角色
        from app.models.ui_test import TestCommonUser
        user_count = await TestCommonUser.filter(
            product=product_role.product,
            role_name=product_role.role_name
        ).count()
        
        if user_count > 0:
            return ResponseSchema.error(
                msg=f"该产品角色已被{user_count}个测试用户使用，无法删除",
                code=400
            )
        
        # 删除产品角色
        await product_role.delete()
        
        return ResponseSchema.success(msg="删除成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)
