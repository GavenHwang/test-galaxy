"""
UI测试用例管理API
"""
from fastapi import APIRouter, Query, Request
from typing import List, Optional
from datetime import datetime
from app.schemas.response import ResponseSchema
from app.schemas.ui_test import (
    TestCaseCreateSchema,
    TestCaseUpdateSchema,
    TestCaseResponseSchema,
    TestStepCreateSchema,
    TestStepUpdateSchema,
    TestStepResponseSchema
)
from app.models.ui_test import (
    TestUICase,
    TestUIStep,
    TestUICasePermission,
    TestUICasesSuitesRelation,
    TestUICaseExecutionRecord,
    CaseStatus,
    CasePriority
)
from tortoise.expressions import Q

router = APIRouter()


def format_datetime(dt: datetime) -> str:
    """格式化时间为 YYYY-MM-DD HH:MM:SS 格式"""
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')


@router.post("", summary="创建测试用例", response_model=ResponseSchema[TestCaseResponseSchema])
async def create_test_case(data: TestCaseCreateSchema, request: Request):
    """
    创建测试用例
    
    业务规则：
    - 自动记录创建人
    - 默认状态为草稿
    """
    try:
        # 获取当前登录用户
        current_user = request.state.current_user
        created_by = current_user.get("username", "system") if current_user else "system"
        
        # 创建测试用例
        test_case = await TestUICase.create(
            name=data.name,
            description=data.description,
            priority=data.priority,
            module=data.module,
            product=data.product,
            tags=data.tags or [],
            status=data.status or CaseStatus.DRAFT,
            precondition=data.precondition,
            expected_result=data.expected_result,
            created_by=created_by
        )
        
        # 构造响应数据
        case_data = TestCaseResponseSchema(
            id=test_case.id,
            name=test_case.name,
            description=test_case.description,
            priority=test_case.priority,
            module=test_case.module,
            product=test_case.product,
            tags=test_case.tags,
            status=test_case.status,
            precondition=test_case.precondition,
            expected_result=test_case.expected_result,
            created_by=test_case.created_by,
            created_time=format_datetime(test_case.created_time),
            updated_time=format_datetime(test_case.updated_time),
            steps=[],
            permission_roles=[],
            execution_count=0,
            last_execution_status=None,
            last_execution_time=None
        )
        
        return ResponseSchema.success(data=case_data, msg="创建成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("", summary="获取测试用例列表")
async def get_test_cases(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    name: Optional[str] = Query(None, description="用例名称模糊搜索"),
    module: Optional[str] = Query(None, description="所属模块精确匹配"),
    priority: Optional[str] = Query(None, description="优先级"),
    status: Optional[str] = Query(None, description="状态"),
    tags: Optional[str] = Query(None, description="标签，逗号分隔"),
    created_by: Optional[str] = Query(None, description="创建人")
):
    """
    分页获取测试用例列表
    
    支持筛选条件：
    - name: 用例名称模糊搜索
    - module: 所属模块精确匹配
    - priority: 优先级（高/中/低）
    - status: 状态（草稿/激活/禁用/归档）
    - tags: 标签（逗号分隔，OR关系）
    - created_by: 创建人
    """
    try:
        # 构建查询条件
        query = TestUICase.all()
        
        if name:
            query = query.filter(name__icontains=name)
        if module:
            query = query.filter(module=module)
        if priority:
            query = query.filter(priority=priority)
        if status:
            query = query.filter(status=status)
        if created_by:
            query = query.filter(created_by=created_by)
        
        # 标签筛选（OR关系）
        if tags:
            tag_list = [t.strip() for t in tags.split(',')]
            # 使用JSON字段查询（需要数据库支持）
            tag_conditions = Q()
            for tag in tag_list:
                tag_conditions |= Q(tags__contains=tag)
            query = query.filter(tag_conditions)
        
        # 查询总数
        total = await query.count()
        
        # 分页查询
        offset = (page - 1) * page_size
        cases = await query.offset(offset).limit(page_size).order_by('-created_time')
        
        # 构造响应数据
        case_list = []
        for case in cases:
            # 查询步骤数量
            step_count = await TestUIStep.filter(test_case_id=case.id).count()
            
            # 查询权限角色
            permissions = await TestUICasePermission.filter(test_case_id=case.id).all()
            permission_roles = [p.role_name for p in permissions]
            
            # 查询执行统计
            execution_count = await TestUICaseExecutionRecord.filter(test_case_id=case.id).count()
            last_execution = await TestUICaseExecutionRecord.filter(
                test_case_id=case.id
            ).order_by('-start_time').first()
            
            case_data = TestCaseResponseSchema(
                id=case.id,
                name=case.name,
                description=case.description,
                priority=case.priority,
                module=case.module,
                product=case.product,
                tags=case.tags,
                status=case.status,
                precondition=case.precondition,
                expected_result=case.expected_result,
                created_by=case.created_by,
                created_time=format_datetime(case.created_time),
                updated_time=format_datetime(case.updated_time),
                steps=[],
                permission_roles=permission_roles,
                execution_count=execution_count,
                last_execution_status=last_execution.status if last_execution else None,
                last_execution_time=format_datetime(last_execution.start_time) if last_execution else None
            )
            case_list.append(case_data)
        
        # 构造分页响应
        result = {
            "items": case_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
        
        return ResponseSchema.success(data=result)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/{case_id}", summary="获取测试用例详情", response_model=ResponseSchema[TestCaseResponseSchema])
async def get_test_case(case_id: int):
    """
    获取测试用例的详细信息，包括所有步骤
    """
    try:
        case = await TestUICase.get_or_none(id=case_id)
        
        if not case:
            return ResponseSchema.error(msg="测试用例不存在", code=404)
        
        # 查询步骤
        steps = await TestUIStep.filter(test_case_id=case.id).order_by('sort_order').all()
        step_list = [
            TestStepResponseSchema(
                id=step.id,
                test_case_id=step.test_case_id,
                step_number=step.step_number,
                action=step.action,
                element_id=step.element_id,
                input_data=step.input_data,
                wait_time=step.wait_time,
                description=step.description,
                sort_order=step.sort_order
            )
            for step in steps
        ]
        
        # 查询权限角色
        permissions = await TestUICasePermission.filter(test_case_id=case.id).all()
        permission_roles = [p.role_name for p in permissions]
        
        # 查询执行统计
        execution_count = await TestUICaseExecutionRecord.filter(test_case_id=case.id).count()
        last_execution = await TestUICaseExecutionRecord.filter(
            test_case_id=case.id
        ).order_by('-start_time').first()
        
        # 构造响应数据
        case_data = TestCaseResponseSchema(
            id=case.id,
            name=case.name,
            description=case.description,
            priority=case.priority,
            module=case.module,
            product=case.product,
            tags=case.tags,
            status=case.status,
            precondition=case.precondition,
            expected_result=case.expected_result,
            created_by=case.created_by,
            created_time=format_datetime(case.created_time),
            updated_time=format_datetime(case.updated_time),
            steps=step_list,
            permission_roles=permission_roles,
            execution_count=execution_count,
            last_execution_status=last_execution.status if last_execution else None,
            last_execution_time=format_datetime(last_execution.start_time) if last_execution else None
        )
        
        return ResponseSchema.success(data=case_data)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.put("/{case_id}", summary="更新测试用例", response_model=ResponseSchema[TestCaseResponseSchema])
async def update_test_case(case_id: int, data: TestCaseUpdateSchema):
    """
    更新测试用例信息
    """
    try:
        case = await TestUICase.get_or_none(id=case_id)
        
        if not case:
            return ResponseSchema.error(msg="测试用例不存在", code=404)
        
        # 构建更新数据
        update_data = data.model_dump(exclude_unset=True)
        
        # 更新字段
        for field, value in update_data.items():
            setattr(case, field, value)
        
        await case.save()
        
        # 查询完整信息
        steps = await TestUIStep.filter(test_case_id=case.id).order_by('sort_order').all()
        step_list = [
            TestStepResponseSchema(
                id=step.id,
                test_case_id=step.test_case_id,
                step_number=step.step_number,
                action=step.action,
                element_id=step.element_id,
                input_data=step.input_data,
                wait_time=step.wait_time,
                description=step.description,
                sort_order=step.sort_order
            )
            for step in steps
        ]
        
        permissions = await TestUICasePermission.filter(test_case_id=case.id).all()
        permission_roles = [p.role_name for p in permissions]
        
        execution_count = await TestUICaseExecutionRecord.filter(test_case_id=case.id).count()
        last_execution = await TestUICaseExecutionRecord.filter(
            test_case_id=case.id
        ).order_by('-start_time').first()
        
        # 构造响应数据
        case_data = TestCaseResponseSchema(
            id=case.id,
            name=case.name,
            description=case.description,
            priority=case.priority,
            module=case.module,
            product=case.product,
            tags=case.tags,
            status=case.status,
            precondition=case.precondition,
            expected_result=case.expected_result,
            created_by=case.created_by,
            created_time=format_datetime(case.created_time),
            updated_time=format_datetime(case.updated_time),
            steps=step_list,
            permission_roles=permission_roles,
            execution_count=execution_count,
            last_execution_status=last_execution.status if last_execution else None,
            last_execution_time=format_datetime(last_execution.start_time) if last_execution else None
        )
        
        return ResponseSchema.success(data=case_data, msg="更新成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.delete("/{case_id}", summary="删除测试用例")
async def delete_test_case(case_id: int, force: bool = Query(False, description="强制删除")):
    """
    删除测试用例
    
    业务规则：
    - 检查是否被套件引用
    - 如force=True，级联删除关联记录
    """
    try:
        case = await TestUICase.get_or_none(id=case_id)
        
        if not case:
            return ResponseSchema.error(msg="测试用例不存在", code=404)
        
        # 检查套件引用
        suite_relations = await TestUICasesSuitesRelation.filter(test_case_id=case_id).count()
        
        if suite_relations > 0 and not force:
            return ResponseSchema.error(
                msg=f"该用例已被{suite_relations}个套件引用，请先解除关联或使用强制删除",
                code=400
            )
        
        # 强制删除时清理关联
        if force:
            await TestUICasesSuitesRelation.filter(test_case_id=case_id).delete()
        
        # 删除步骤
        await TestUIStep.filter(test_case_id=case_id).delete()
        
        # 删除权限
        await TestUICasePermission.filter(test_case_id=case_id).delete()
        
        # 删除用例
        await case.delete()
        
        return ResponseSchema.success(msg="删除成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/{case_id}/copy", summary="复制测试用例", response_model=ResponseSchema[TestCaseResponseSchema])
async def copy_test_case(case_id: int, request: Request):
    """
    复制测试用例
    
    业务规则：
    - 复制用例基本信息和所有步骤
    - 新用例名称添加"副本"后缀
    - 新用例状态为草稿
    - 不复制执行历史和权限
    """
    try:
        # 获取原用例
        original_case = await TestUICase.get_or_none(id=case_id)
        
        if not original_case:
            return ResponseSchema.error(msg="测试用例不存在", code=404)
        
        # 获取当前用户
        current_user = request.state.current_user
        created_by = current_user.get("username", "system") if current_user else "system"
        
        # 创建新用例
        new_case = await TestUICase.create(
            name=f"{original_case.name} 副本",
            description=original_case.description,
            priority=original_case.priority,
            module=original_case.module,
            product=original_case.product,
            tags=original_case.tags,
            status=CaseStatus.DRAFT,
            precondition=original_case.precondition,
            expected_result=original_case.expected_result,
            created_by=created_by
        )
        
        # 复制步骤
        original_steps = await TestUIStep.filter(test_case_id=case_id).order_by('sort_order').all()
        for step in original_steps:
            await TestUIStep.create(
                test_case_id=new_case.id,
                step_number=step.step_number,
                action=step.action,
                element_id=step.element_id,
                input_data=step.input_data,
                wait_time=step.wait_time,
                description=step.description,
                sort_order=step.sort_order
            )
        
        # 查询新用例的步骤
        steps = await TestUIStep.filter(test_case_id=new_case.id).order_by('sort_order').all()
        step_list = [
            TestStepResponseSchema(
                id=step.id,
                test_case_id=step.test_case_id,
                step_number=step.step_number,
                action=step.action,
                element_id=step.element_id,
                input_data=step.input_data,
                wait_time=step.wait_time,
                description=step.description,
                sort_order=step.sort_order
            )
            for step in steps
        ]
        
        # 构造响应数据
        case_data = TestCaseResponseSchema(
            id=new_case.id,
            name=new_case.name,
            description=new_case.description,
            priority=new_case.priority,
            module=new_case.module,
            product=new_case.product,
            tags=new_case.tags,
            status=new_case.status,
            precondition=new_case.precondition,
            expected_result=new_case.expected_result,
            created_by=new_case.created_by,
            created_time=format_datetime(new_case.created_time),
            updated_time=format_datetime(new_case.updated_time),
            steps=step_list,
            permission_roles=[],
            execution_count=0,
            last_execution_status=None,
            last_execution_time=None
        )
        
        return ResponseSchema.success(data=case_data, msg="复制成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.patch("/{case_id}/status", summary="更新用例状态")
async def update_case_status(case_id: int, status: CaseStatus):
    """
    更新测试用例状态
    """
    try:
        case = await TestUICase.get_or_none(id=case_id)
        
        if not case:
            return ResponseSchema.error(msg="测试用例不存在", code=404)
        
        case.status = status
        await case.save()
        
        return ResponseSchema.success(msg="状态更新成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


# ========== 测试步骤管理 ==========

@router.get("/{case_id}/steps", summary="获取测试步骤列表")
async def get_test_steps(case_id: int):
    """
    获取测试用例的所有步骤
    """
    try:
        case = await TestUICase.get_or_none(id=case_id)
        
        if not case:
            return ResponseSchema.error(msg="测试用例不存在", code=404)
        
        steps = await TestUIStep.filter(test_case_id=case_id).order_by('sort_order').all()
        
        step_list = [
            TestStepResponseSchema(
                id=step.id,
                test_case_id=step.test_case_id,
                step_number=step.step_number,
                action=step.action,
                element_id=step.element_id,
                input_data=step.input_data,
                wait_time=step.wait_time,
                description=step.description,
                sort_order=step.sort_order
            )
            for step in steps
        ]
        
        return ResponseSchema.success(data=step_list)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/{case_id}/steps", summary="创建测试步骤", response_model=ResponseSchema[TestStepResponseSchema])
async def create_test_step(case_id: int, data: TestStepCreateSchema):
    """
    为测试用例创建新步骤
    """
    try:
        case = await TestUICase.get_or_none(id=case_id)
        
        if not case:
            return ResponseSchema.error(msg="测试用例不存在", code=404)
        
        # 获取当前最大sort_order
        max_sort = await TestUIStep.filter(test_case_id=case_id).count()
        
        # 创建步骤
        step = await TestUIStep.create(
            test_case_id=case_id,
            step_number=max_sort + 1,
            action=data.action,
            element_id=data.element_id,
            input_data=data.input_data,
            wait_time=data.wait_time,
            description=data.description,
            sort_order=max_sort + 1
        )
        
        step_data = TestStepResponseSchema(
            id=step.id,
            test_case_id=step.test_case_id,
            step_number=step.step_number,
            action=step.action,
            element_id=step.element_id,
            input_data=step.input_data,
            wait_time=step.wait_time,
            description=step.description,
            sort_order=step.sort_order
        )
        
        return ResponseSchema.success(data=step_data, msg="创建成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.put("/steps/{step_id}", summary="更新测试步骤", response_model=ResponseSchema[TestStepResponseSchema])
async def update_test_step(step_id: int, data: TestStepUpdateSchema):
    """
    更新测试步骤
    """
    try:
        step = await TestUIStep.get_or_none(id=step_id)
        
        if not step:
            return ResponseSchema.error(msg="测试步骤不存在", code=404)
        
        # 构建更新数据
        update_data = data.model_dump(exclude_unset=True)
        
        # 更新字段
        for field, value in update_data.items():
            setattr(step, field, value)
        
        await step.save()
        
        step_data = TestStepResponseSchema(
            id=step.id,
            test_case_id=step.test_case_id,
            step_number=step.step_number,
            action=step.action,
            element_id=step.element_id,
            input_data=step.input_data,
            wait_time=step.wait_time,
            description=step.description,
            sort_order=step.sort_order
        )
        
        return ResponseSchema.success(data=step_data, msg="更新成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.delete("/steps/{step_id}", summary="删除测试步骤")
async def delete_test_step(step_id: int):
    """
    删除测试步骤
    """
    try:
        step = await TestUIStep.get_or_none(id=step_id)
        
        if not step:
            return ResponseSchema.error(msg="测试步骤不存在", code=404)
        
        case_id = step.test_case_id
        sort_order = step.sort_order
        
        # 删除步骤
        await step.delete()
        
        # 重新排序后续步骤
        following_steps = await TestUIStep.filter(
            test_case_id=case_id,
            sort_order__gt=sort_order
        ).all()
        
        for s in following_steps:
            s.sort_order -= 1
            s.step_number -= 1
            await s.save()
        
        return ResponseSchema.success(msg="删除成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/{case_id}/steps/reorder", summary="调整步骤顺序")
async def reorder_steps(case_id: int, step_ids: List[int]):
    """
    调整测试步骤的执行顺序
    
    参数：step_ids - 按新顺序排列的步骤ID数组
    """
    try:
        case = await TestUICase.get_or_none(id=case_id)
        
        if not case:
            return ResponseSchema.error(msg="测试用例不存在", code=404)
        
        # 更新步骤顺序
        for index, step_id in enumerate(step_ids):
            step = await TestUIStep.get_or_none(id=step_id, test_case_id=case_id)
            if step:
                step.sort_order = index + 1
                step.step_number = index + 1
                await step.save()
        
        return ResponseSchema.success(msg="顺序调整成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


# ========== 权限管理 ==========

@router.get("/{case_id}/permissions", summary="获取用例权限")
async def get_case_permissions(case_id: int):
    """
    获取用例的权限角色列表
    """
    try:
        case = await TestUICase.get_or_none(id=case_id)
        
        if not case:
            return ResponseSchema.error(msg="测试用例不存在", code=404)
        
        permissions = await TestUICasePermission.filter(test_case_id=case_id).all()
        roles = [p.role_name for p in permissions]
        
        return ResponseSchema.success(data=roles)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/{case_id}/permissions", summary="设置用例权限")
async def set_case_permissions(case_id: int, roles: List[str]):
    """
    设置用例的权限角色
    """
    try:
        case = await TestUICase.get_or_none(id=case_id)
        
        if not case:
            return ResponseSchema.error(msg="测试用例不存在", code=404)
        
        # 删除现有权限
        await TestUICasePermission.filter(test_case_id=case_id).delete()
        
        # 添加新权限
        for role in roles:
            await TestUICasePermission.create(
                test_case_id=case_id,
                role_name=role
            )
        
        return ResponseSchema.success(msg="权限设置成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


# ========== 执行历史 ==========

@router.get("/{case_id}/executions", summary="获取执行历史")
async def get_case_executions(
    case_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    获取测试用例的执行历史记录
    """
    try:
        case = await TestUICase.get_or_none(id=case_id)
        
        if not case:
            return ResponseSchema.error(msg="测试用例不存在", code=404)
        
        # 查询总数
        total = await TestUICaseExecutionRecord.filter(test_case_id=case_id).count()
        
        # 分页查询
        offset = (page - 1) * page_size
        records = await TestUICaseExecutionRecord.filter(
            test_case_id=case_id
        ).offset(offset).limit(page_size).order_by('-start_time').all()
        
        record_list = [
            {
                "id": record.id,
                "test_case_id": record.test_case_id,
                "test_report_id": record.test_report_id,
                "status": record.status,
                "start_time": record.start_time,
                "end_time": record.end_time,
                "duration": record.duration,
                "error_message": record.error_message,
                "screenshot_path": record.screenshot_path
            }
            for record in records
        ]
        
        result = {
            "items": record_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
        
        return ResponseSchema.success(data=result)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/{case_id}/execution-trend", summary="获取执行趋势")
async def get_execution_trend(case_id: int, days: int = Query(30, ge=1, le=90)):
    """
    获取测试用例的执行趋势数据
    """
    try:
        case = await TestUICase.get_or_none(id=case_id)
        
        if not case:
            return ResponseSchema.error(msg="测试用例不存在", code=404)
        
        # 这里返回模拟数据，实际应该查询数据库统计
        # TODO: 实现真实的趋势统计
        trend_data = {
            "pass_rate_trend": [],
            "avg_duration_trend": [],
            "failure_reasons": {}
        }
        
        return ResponseSchema.success(data=trend_data)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


# ========== 批量操作 ==========

@router.post("/batch-update-status", summary="批量更新状态")
async def batch_update_status(case_ids: List[int], status: CaseStatus):
    """
    批量更新测试用例状态
    """
    try:
        updated_count = await TestUICase.filter(id__in=case_ids).update(status=status)
        
        return ResponseSchema.success(
            data={"updated_count": updated_count},
            msg=f"成功更新{updated_count}个用例"
        )
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/modules/list", summary="获取测试用例模块列表")
async def get_case_modules():
    """
    获取所有不重复的测试用例模块列表，用于下拉选择器
    """
    try:
        # 查询所有不重复的模块
        modules = await TestUICase.all().distinct().values_list('module', flat=True)
        
        # 过滤空值并排序
        modules = sorted([m for m in modules if m])
        
        return ResponseSchema.success(data=modules)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)
