"""
UI页面元素管理API
"""
from fastapi import APIRouter, Query, Request
from typing import List, Optional
from datetime import datetime
from app.schemas.response import ResponseSchema
from app.schemas.ui_test import (
    UIElementCreateSchema,
    UIElementUpdateSchema,
    UIElementResponseSchema,
    UIElementBatchCreateSchema,
    ElementPermissionSchema
)
from app.models.ui_test import (
    TestUIElement, 
    TestUIElementPermission, 
    TestUIStep,
    TestCommonUser,
    SelectorType
)

router = APIRouter()


def format_datetime(dt: datetime) -> str:
    """格式化时间为 YYYY-MM-DD HH:MM:SS 格式"""
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')


@router.post("", summary="创建页面元素", response_model=ResponseSchema[UIElementResponseSchema])
async def create_element(data: UIElementCreateSchema, request: Request):
    """
    创建页面元素
    
    业务规则：
    - 同一页面下元素名称唯一
    - selector_value根据selector_type进行格式验证
    - 自动记录创建人
    """
    try:
        # 获取当前登录用户
        current_user = request.state.current_user
        created_by = current_user.get("username", "system") if current_user else "system"
        
        # 检查同一产品下同一页面的元素名称是否已存在
        exists = await TestUIElement.filter(
            name=data.name,
            page=data.page,
            product=data.product
        ).exists()
        
        if exists:
            return ResponseSchema.error(
                msg=f"元素名称'{data.name}'在产品'{data.product}'的页面'{data.page}'下已存在",
                code=400
            )
        
        # 基本格式验证
        if data.selector_type == SelectorType.XPATH:
            if not (data.selector_value.startswith('/') or data.selector_value.startswith('//')):
                return ResponseSchema.error(msg="XPATH定位器必须以/或//开头", code=400)
        elif data.selector_type in [SelectorType.ID, SelectorType.NAME]:
            if ' ' in data.selector_value:
                return ResponseSchema.error(msg="ID/NAME定位器不能包含空格", code=400)
        
        # 创建元素
        element = await TestUIElement.create(
            name=data.name,
            selector_type=data.selector_type,
            selector_value=data.selector_value,
            page=data.page,
            module=data.module,
            product=data.product,
            description=data.description,
            created_by=created_by
        )
        
        # 构造响应数据
        element_data = UIElementResponseSchema(
            id=element.id,
            name=element.name,
            selector_type=element.selector_type,
            selector_value=element.selector_value,
            page=element.page,
            module=element.module,
            product=element.product,
            description=element.description,
            created_by=element.created_by,
            created_time=format_datetime(element.created_time),
            updated_time=format_datetime(element.updated_time),
            related_cases_count=0,
            permission_roles=[]
        )
        
        return ResponseSchema.success(data=element_data, msg="创建成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("", summary="获取页面元素列表")
async def get_elements(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    name: Optional[str] = Query(None, description="元素名称模糊搜索"),
    page_url: Optional[str] = Query(None, description="所属页面精确匹配", alias="page"),
    module: Optional[str] = Query(None, description="所属模块精确匹配"),
    selector_type: Optional[str] = Query(None, description="定位器类型精确匹配"),
    product: Optional[str] = Query(None, description="所属产品精确匹配")
):
    """
    分页获取页面元素列表
    
    支持筛选条件：
    - name: 元素名称模糊搜索
    - page: 所属页面精确匹配
    - module: 所属模块精确匹配
    - selector_type: 定位器类型精确匹配
    - product: 所属产品精确匹配
    """
    try:
        # 构建查询条件
        query = TestUIElement.all()
        
        if name:
            query = query.filter(name__icontains=name)
        if page_url:
            query = query.filter(page=page_url)
        if module:
            query = query.filter(module=module)
        if selector_type:
            query = query.filter(selector_type=selector_type)
        if product:
            query = query.filter(product=product)
        
        # 查询总数
        total = await query.count()
        
        # 分页查询
        offset = (page - 1) * page_size
        elements = await query.offset(offset).limit(page_size).order_by('-created_time')
        
        # 构造响应数据
        element_list = []
        for element in elements:
            # 查询关联用例数量
            related_cases_count = await TestUIStep.filter(element_id=element.id).count()
            
            # 查询权限角色
            permissions = await TestUIElementPermission.filter(element_id=element.id).all()
            permission_roles = [p.role_name for p in permissions]
            
            element_data = UIElementResponseSchema(
                id=element.id,
                name=element.name,
                selector_type=element.selector_type,
                selector_value=element.selector_value,
                page=element.page,
                module=element.module,
                product=element.product,
                description=element.description,
                created_by=element.created_by,
                created_time=format_datetime(element.created_time),
                updated_time=format_datetime(element.updated_time),
                related_cases_count=related_cases_count,
                permission_roles=permission_roles
            )
            element_list.append(element_data)
        
        # 构造分页响应
        result = {
            "items": element_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
        
        return ResponseSchema.success(data=result)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/{element_id}", summary="获取单个页面元素详情", response_model=ResponseSchema[UIElementResponseSchema])
async def get_element(element_id: int):
    """
    获取单个页面元素的详细信息
    """
    try:
        element = await TestUIElement.get_or_none(id=element_id)
        
        if not element:
            return ResponseSchema.error(msg="页面元素不存在", code=404)
        
        # 查询关联用例数量
        related_cases_count = await TestUIStep.filter(element_id=element.id).count()
        
        # 查询权限角色
        permissions = await TestUIElementPermission.filter(element_id=element.id).all()
        permission_roles = [p.role_name for p in permissions]
        
        # 构造响应数据
        element_data = UIElementResponseSchema(
            id=element.id,
            name=element.name,
            selector_type=element.selector_type,
            selector_value=element.selector_value,
            page=element.page,
            module=element.module,
            description=element.description,
            created_by=element.created_by,
            created_time=format_datetime(element.created_time),
            updated_time=format_datetime(element.updated_time),
            related_cases_count=related_cases_count,
            permission_roles=permission_roles
        )
        
        return ResponseSchema.success(data=element_data)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.put("/{element_id}", summary="更新页面元素", response_model=ResponseSchema[UIElementResponseSchema])
async def update_element(element_id: int, data: UIElementUpdateSchema):
    """
    更新页面元素信息
    
    业务规则：
    - 支持部分字段更新
    - 元素名称修改时重新检查唯一性
    """
    try:
        element = await TestUIElement.get_or_none(id=element_id)
        
        if not element:
            return ResponseSchema.error(msg="页面元素不存在", code=404)
        
        # 构建更新数据
        update_data = data.model_dump(exclude_unset=True)
        
        # 如果修改了元素名称或页面，检查唯一性
        if 'name' in update_data or 'page' in update_data:
            new_name = update_data.get('name', element.name)
            new_page = update_data.get('page', element.page)
            
            # 排除自己检查是否存在重复
            exists = await TestUIElement.filter(
                name=new_name,
                page=new_page
            ).exclude(id=element_id).exists()
            
            if exists:
                return ResponseSchema.error(
                    msg=f"元素名称'{new_name}'在页面'{new_page}'下已存在",
                    code=400
                )
        
        # 格式验证
        if 'selector_type' in update_data and 'selector_value' in update_data:
            selector_type = update_data['selector_type']
            selector_value = update_data['selector_value']
            
            if selector_type == SelectorType.XPATH:
                if not (selector_value.startswith('/') or selector_value.startswith('//')):
                    return ResponseSchema.error(msg="XPATH定位器必须以/或//开头", code=400)
            elif selector_type in [SelectorType.ID, SelectorType.NAME]:
                if ' ' in selector_value:
                    return ResponseSchema.error(msg="ID/NAME定位器不能包含空格", code=400)
        
        # 更新字段
        for field, value in update_data.items():
            setattr(element, field, value)
        
        await element.save()
        
        # 查询关联信息
        related_cases_count = await TestUIStep.filter(element_id=element.id).count()
        permissions = await TestUIElementPermission.filter(element_id=element.id).all()
        permission_roles = [p.role_name for p in permissions]
        
        # 构造响应数据
        element_data = UIElementResponseSchema(
            id=element.id,
            name=element.name,
            selector_type=element.selector_type,
            selector_value=element.selector_value,
            page=element.page,
            module=element.module,
            description=element.description,
            created_by=element.created_by,
            created_time=format_datetime(element.created_time),
            updated_time=format_datetime(element.updated_time),
            related_cases_count=related_cases_count,
            permission_roles=permission_roles
        )
        
        return ResponseSchema.success(data=element_data, msg="更新成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.delete("/{element_id}", summary="删除页面元素")
async def delete_element(element_id: int):
    """
    删除页面元素
    
    业务规则：
    - 检查是否被测试步骤引用
    - 如被引用，返回错误提示
    """
    try:
        element = await TestUIElement.get_or_none(id=element_id)
        
        if not element:
            return ResponseSchema.error(msg="页面元素不存在", code=404)
        
        # 检查是否被测试步骤引用
        related_count = await TestUIStep.filter(element_id=element.id).count()
        
        if related_count > 0:
            return ResponseSchema.error(
                msg=f"该元素已被{related_count}个测试用例引用，无法删除",
                code=400
            )
        
        # 删除权限关联
        await TestUIElementPermission.filter(element_id=element.id).delete()
        
        # 删除元素
        await element.delete()
        
        return ResponseSchema.success(msg="删除成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/batch", summary="批量创建页面元素")
async def batch_create_elements(data: UIElementBatchCreateSchema, request: Request):
    """
    批量创建页面元素
    
    用于Excel导入功能
    """
    try:
        # 获取当前登录用户
        current_user = request.state.current_user
        created_by = current_user.get("username", "system") if current_user else "system"
        
        created_count = 0
        skipped_count = 0
        errors = []
        
        for element_data in data.elements:
            try:
                # 检查是否已存在
                exists = await TestUIElement.filter(
                    name=element_data.name,
                    page=element_data.page
                ).exists()
                
                if exists:
                    skipped_count += 1
                    errors.append(f"元素'{element_data.name}'在页面'{element_data.page}'下已存在，跳过")
                    continue
                
                # 创建元素
                await TestUIElement.create(
                    name=element_data.name,
                    selector_type=element_data.selector_type,
                    selector_value=element_data.selector_value,
                    page=element_data.page,
                    module=element_data.module,
                    description=element_data.description,
                    created_by=created_by
                )
                created_count += 1
                
            except Exception as e:
                errors.append(f"创建元素'{element_data.name}'失败: {str(e)}")
                continue
        
        result = {
            "created_count": created_count,
            "skipped_count": skipped_count,
            "errors": errors
        }
        
        return ResponseSchema.success(
            data=result,
            msg=f"批量创建完成，成功{created_count}个，跳过{skipped_count}个"
        )
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/{element_id}/related-cases", summary="获取关联的测试用例")
async def get_related_cases(element_id: int):
    """
    获取引用该元素的测试用例列表
    """
    try:
        element = await TestUIElement.get_or_none(id=element_id)
        
        if not element:
            return ResponseSchema.error(msg="页面元素不存在", code=404)
        
        # 查询引用该元素的步骤
        steps = await TestUIStep.filter(element_id=element_id).prefetch_related('test_case').all()
        
        # 构造用例列表（去重）
        cases_dict = {}
        for step in steps:
            case = step.test_case
            if case.id not in cases_dict:
                cases_dict[case.id] = {
                    "case_id": case.id,
                    "case_name": case.name,
                    "step_count": 1,
                    "steps": [{"step_id": step.id, "step_number": step.step_number, "description": step.description}]
                }
            else:
                cases_dict[case.id]["step_count"] += 1
                cases_dict[case.id]["steps"].append({
                    "step_id": step.id,
                    "step_number": step.step_number,
                    "description": step.description
                })
        
        cases = list(cases_dict.values())
        
        return ResponseSchema.success(data=cases)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/{element_id}/permissions", summary="获取元素权限")
async def get_element_permissions(element_id: int):
    """
    获取元素的权限角色列表
    """
    try:
        element = await TestUIElement.get_or_none(id=element_id)
        
        if not element:
            return ResponseSchema.error(msg="页面元素不存在", code=404)
        
        # 查询权限
        permissions = await TestUIElementPermission.filter(element_id=element_id).all()
        roles = [p.role_name for p in permissions]
        
        return ResponseSchema.success(data=roles)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/{element_id}/permissions", summary="设置元素权限")
async def set_element_permissions(element_id: int, data: ElementPermissionSchema):
    """
    设置元素的权限角色
    
    业务规则：
    - 先删除现有权限，再添加新权限
    """
    try:
        element = await TestUIElement.get_or_none(id=element_id)
        
        if not element:
            return ResponseSchema.error(msg="页面元素不存在", code=404)
        
        # 删除现有权限
        await TestUIElementPermission.filter(element_id=element_id).delete()
        
        # 添加新权限
        for role in data.roles:
            await TestUIElementPermission.create(
                element_id=element_id,
                role_name=role
            )
        
        return ResponseSchema.success(msg="权限设置成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/pages/list", summary="获取页面列表")
async def get_pages():
    """
    获取所有不重复的页面列表，用于下拉选择器
    """
    try:
        # 查询所有不重复的页面
        pages = await TestUIElement.all().distinct().values_list('page', flat=True)
        
        # 过滤空值并排序
        pages = sorted([p for p in pages if p])
        
        return ResponseSchema.success(data=pages)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/modules/list", summary="获取模块列表")
async def get_modules():
    """
    获取所有不重复的模块列表，用于下拉选择器
    """
    try:
        # 查询所有不重复的模块
        modules = await TestUIElement.all().distinct().values_list('module', flat=True)
        
        # 过滤空值并排序
        modules = sorted([m for m in modules if m])
        
        return ResponseSchema.success(data=modules)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)
