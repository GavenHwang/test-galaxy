"""
产品管理API
"""
from fastapi import APIRouter, Query, Request
from typing import Optional
from datetime import datetime
from app.schemas.response import ResponseSchema
from app.schemas.ui_test import (
    ProductCreateSchema,
    ProductUpdateSchema,
    ProductResponseSchema,
    ProductListParams,
    ProductStatusUpdateSchema
)
from app.models.ui_test import (
    TestProduct,
    ProductStatus,
    TestUIElement,
    TestUICase,
    TestUICaseSuite,
    TestUITask,
    TestUIReport
)

router = APIRouter()


def format_datetime(dt: datetime) -> str:
    """格式化时间为 YYYY-MM-DD HH:MM:SS 格式"""
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')


@router.post("", summary="创建产品", response_model=ResponseSchema[ProductResponseSchema])
async def create_product(data: ProductCreateSchema, request: Request):
    """
    创建产品
    
    业务规则：
    - 产品名称唯一
    - 产品编码唯一（如果提供）
    - 自动记录创建人
    """
    try:
        # 获取当前登录用户
        current_user = request.state.current_user
        created_by = current_user.get("username", "system") if current_user else "system"
        
        # 检查产品名称是否已存在
        exists = await TestProduct.filter(name=data.name).exists()
        if exists:
            return ResponseSchema.error(
                msg=f"产品名称'{data.name}'已存在",
                code=400
            )
        
        # 检查产品编码是否已存在（如果提供）
        if data.code:
            exists = await TestProduct.filter(code=data.code).exists()
            if exists:
                return ResponseSchema.error(
                    msg=f"产品编码'{data.code}'已存在",
                    code=400
                )
        
        # 创建产品
        product = await TestProduct.create(
            name=data.name,
            code=data.code,
            status=data.status,
            sort_order=data.sort_order if data.sort_order is not None else 0,
            description=data.description,
            created_by=created_by
        )
        
        # 构造响应数据
        product_data = ProductResponseSchema(
            id=product.id,
            name=product.name,
            code=product.code,
            status=product.status,
            sort_order=product.sort_order,
            description=product.description,
            created_by=product.created_by,
            created_time=format_datetime(product.created_time),
            updated_time=format_datetime(product.updated_time)
        )
        
        return ResponseSchema.success(data=product_data, msg="创建成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("", summary="获取产品列表（分页）")
async def get_products(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    name: Optional[str] = Query(None, description="产品名称模糊搜索"),
    status: Optional[str] = Query(None, description="状态筛选")
):
    """
    分页获取产品列表
    
    支持筛选条件：
    - name: 产品名称模糊搜索
    - status: 状态筛选
    """
    try:
        # 构建查询条件
        query = TestProduct.all()
        
        if name:
            query = query.filter(name__icontains=name)
        if status:
            query = query.filter(status=status)
        
        # 查询总数
        total = await query.count()
        
        # 分页查询，按sort_order升序，相同时按创建时间倒序
        offset = (page - 1) * page_size
        products = await query.offset(offset).limit(page_size).order_by('sort_order', '-created_time')
        
        # 构造响应数据
        product_list = []
        for product in products:
            product_list.append(
                ProductResponseSchema(
                    id=product.id,
                    name=product.name,
                    code=product.code,
                    status=product.status,
                    sort_order=product.sort_order,
                    description=product.description,
                    created_by=product.created_by,
                    created_time=format_datetime(product.created_time),
                    updated_time=format_datetime(product.updated_time)
                )
            )
        
        # 构造分页响应
        result = {
            "items": product_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
        
        return ResponseSchema.success(data=result)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/all", summary="获取所有启用的产品")
async def get_all_products():
    """
    获取所有启用的产品（不分页）
    
    用途：供下拉选择器使用
    返回数据按sort_order升序排序
    """
    try:
        # 查询所有启用的产品
        products = await TestProduct.filter(status=ProductStatus.ENABLED).order_by('sort_order')
        
        # 构造响应数据
        product_list = []
        for product in products:
            product_list.append({
                "name": product.name,
                "code": product.code,
                "sort_order": product.sort_order
            })
        
        return ResponseSchema.success(data=product_list)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/{product_id}", summary="获取单个产品详情", response_model=ResponseSchema[ProductResponseSchema])
async def get_product(product_id: int):
    """
    获取单个产品的详细信息
    """
    try:
        product = await TestProduct.get_or_none(id=product_id)
        
        if not product:
            return ResponseSchema.error(msg="产品不存在", code=404)
        
        # 构造响应数据
        product_data = ProductResponseSchema(
            id=product.id,
            name=product.name,
            code=product.code,
            status=product.status,
            sort_order=product.sort_order,
            description=product.description,
            created_by=product.created_by,
            created_time=format_datetime(product.created_time),
            updated_time=format_datetime(product.updated_time)
        )
        
        return ResponseSchema.success(data=product_data)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.put("/{product_id}", summary="更新产品", response_model=ResponseSchema[ProductResponseSchema])
async def update_product(product_id: int, data: ProductUpdateSchema):
    """
    更新产品信息
    
    业务规则：
    - 支持部分字段更新
    - 名称和编码修改时需重新检查唯一性
    """
    try:
        product = await TestProduct.get_or_none(id=product_id)
        
        if not product:
            return ResponseSchema.error(msg="产品不存在", code=404)
        
        # 构建更新数据
        update_data = data.model_dump(exclude_unset=True)
        
        # 如果修改了名称，检查唯一性
        if 'name' in update_data:
            exists = await TestProduct.filter(name=update_data['name']).exclude(id=product_id).exists()
            if exists:
                return ResponseSchema.error(
                    msg=f"产品名称'{update_data['name']}'已存在",
                    code=400
                )
        
        # 如果修改了编码，检查唯一性
        if 'code' in update_data and update_data['code']:
            exists = await TestProduct.filter(code=update_data['code']).exclude(id=product_id).exists()
            if exists:
                return ResponseSchema.error(
                    msg=f"产品编码'{update_data['code']}'已存在",
                    code=400
                )
        
        # 更新字段
        for field, value in update_data.items():
            setattr(product, field, value)
        
        await product.save()
        
        # 构造响应数据
        product_data = ProductResponseSchema(
            id=product.id,
            name=product.name,
            code=product.code,
            status=product.status,
            sort_order=product.sort_order,
            description=product.description,
            created_by=product.created_by,
            created_time=format_datetime(product.created_time),
            updated_time=format_datetime(product.updated_time)
        )
        
        return ResponseSchema.success(data=product_data, msg="更新成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.patch("/{product_id}/status", summary="更新产品状态", response_model=ResponseSchema[ProductResponseSchema])
async def update_product_status(product_id: int, data: ProductStatusUpdateSchema):
    """
    更新产品状态
    
    业务规则：
    - 仅更新status字段
    """
    try:
        product = await TestProduct.get_or_none(id=product_id)
        
        if not product:
            return ResponseSchema.error(msg="产品不存在", code=404)
        
        # 更新状态
        product.status = data.status
        await product.save()
        
        # 构造响应数据
        product_data = ProductResponseSchema(
            id=product.id,
            name=product.name,
            code=product.code,
            status=product.status,
            sort_order=product.sort_order,
            description=product.description,
            created_by=product.created_by,
            created_time=format_datetime(product.created_time),
            updated_time=format_datetime(product.updated_time)
        )
        
        return ResponseSchema.success(data=product_data, msg="状态更新成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.delete("/{product_id}", summary="删除产品")
async def delete_product(product_id: int):
    """
    删除产品
    
    业务规则：
    - 检查是否有元素、用例、套件、测试单、报告关联此产品
    - 如有关联，返回错误信息并拒绝删除
    """
    try:
        product = await TestProduct.get_or_none(id=product_id)
        
        if not product:
            return ResponseSchema.error(msg="产品不存在", code=404)
        
        # 检查关联
        elements_count = await TestUIElement.filter(product=product.name).count()
        cases_count = await TestUICase.filter(product=product.name).count()
        suites_count = await TestUICaseSuite.filter(product=product.name).count()
        tasks_count = await TestUITask.filter(product=product.name).count()
        reports_count = await TestUIReport.filter(product=product.name).count()
        
        if elements_count > 0 or cases_count > 0 or suites_count > 0 or tasks_count > 0 or reports_count > 0:
            return ResponseSchema.error(
                msg=f"该产品已被{elements_count}个元素、{cases_count}个用例、{suites_count}个套件、{tasks_count}个测试单、{reports_count}个报告使用，无法删除",
                code=400
            )
        
        # 删除产品
        await product.delete()
        
        return ResponseSchema.success(msg="删除成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)
