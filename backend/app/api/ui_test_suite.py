"""
UI测试套件管理API
"""
from fastapi import APIRouter, Query, Request
from typing import List, Optional
from datetime import datetime
from app.schemas.response import ResponseSchema
from app.schemas.ui_test import (
    TestSuiteCreateSchema,
    TestSuiteUpdateSchema,
    TestSuiteResponseSchema
)
from app.models.ui_test import (
    TestUICaseSuite,
    TestUICasesSuitesRelation,
    TestUICase,
    TestUITaskContent,
    CaseStatus
)
from tortoise.expressions import Q

router = APIRouter()


def format_datetime(dt: datetime) -> str:
    """格式化时间为 YYYY-MM-DD HH:MM:SS 格式"""
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')


@router.post("", summary="创建测试套件", response_model=ResponseSchema[TestSuiteResponseSchema])
async def create_test_suite(data: TestSuiteCreateSchema, request: Request):
    """
    创建测试套件
    """
    try:
        current_user = request.state.current_user
        created_by = current_user.get("username", "system") if current_user else "system"
        
        # 创建套件
        suite = await TestUICaseSuite.create(
            name=data.name,
            description=data.description,
            product=data.product,
            filter_conditions=data.filter_conditions.model_dump() if data.filter_conditions else {},
            created_by=created_by
        )
        
        suite_data = TestSuiteResponseSchema(
            id=suite.id,
            name=suite.name,
            description=suite.description,
            product=suite.product,
            filter_conditions=suite.filter_conditions,
            created_by=suite.created_by,
            created_time=format_datetime(suite.created_time),
            updated_time=format_datetime(suite.updated_time),
            case_count=0,
            cases=None
        )
        
        return ResponseSchema.success(data=suite_data, msg="创建成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("", summary="获取测试套件列表")
async def get_test_suites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    name: Optional[str] = Query(None),
    created_by: Optional[str] = Query(None)
):
    """
    分页获取测试套件列表
    """
    try:
        query = TestUICaseSuite.all()
        
        if name:
            query = query.filter(name__icontains=name)
        if created_by:
            query = query.filter(created_by=created_by)
        
        total = await query.count()
        offset = (page - 1) * page_size
        suites = await query.offset(offset).limit(page_size).order_by('-created_time')
        
        suite_list = []
        for suite in suites:
            case_count = await TestUICasesSuitesRelation.filter(test_suite_id=suite.id).count()
            
            suite_data = TestSuiteResponseSchema(
                id=suite.id,
                name=suite.name,
                description=suite.description,
                product=suite.product,
                filter_conditions=suite.filter_conditions,
                created_by=suite.created_by,
                created_time=format_datetime(suite.created_time),
                updated_time=format_datetime(suite.updated_time),
                case_count=case_count,
                cases=None
            )
            suite_list.append(suite_data)
        
        result = {
            "items": suite_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
        
        return ResponseSchema.success(data=result)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/{suite_id}", summary="获取测试套件详情")
async def get_test_suite(suite_id: int):
    """
    获取测试套件详细信息，包括关联的用例
    """
    try:
        suite = await TestUICaseSuite.get_or_none(id=suite_id)
        
        if not suite:
            return ResponseSchema.error(msg="测试套件不存在", code=404)
        
        # 查询关联用例
        relations = await TestUICasesSuitesRelation.filter(test_suite_id=suite_id).prefetch_related('test_case').all()
        cases = [
            {
                "id": rel.test_case.id,
                "name": rel.test_case.name,
                "priority": rel.test_case.priority,
                "product": rel.test_case.product,
                "status": rel.test_case.status,
                "sort_order": rel.sort_order
            }
            for rel in relations
        ]
        
        suite_data = TestSuiteResponseSchema(
            id=suite.id,
            name=suite.name,
            description=suite.description,
            product=suite.product,
            filter_conditions=suite.filter_conditions,
            created_by=suite.created_by,
            created_time=format_datetime(suite.created_time),
            updated_time=format_datetime(suite.updated_time),
            case_count=len(cases),
            cases=None  # 不返回用例列表，使用单独的API获取
        )
        
        return ResponseSchema.success(data=suite_data)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.put("/{suite_id}", summary="更新测试套件")
async def update_test_suite(suite_id: int, data: TestSuiteUpdateSchema):
    """
    更新测试套件信息
    """
    try:
        suite = await TestUICaseSuite.get_or_none(id=suite_id)
        
        if not suite:
            return ResponseSchema.error(msg="测试套件不存在", code=404)
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(suite, field, value)
        
        await suite.save()
        
        case_count = await TestUICasesSuitesRelation.filter(test_suite_id=suite_id).count()
        
        suite_data = TestSuiteResponseSchema(
            id=suite.id,
            name=suite.name,
            description=suite.description,
            product=suite.product,
            filter_conditions=suite.filter_conditions,
            created_by=suite.created_by,
            created_time=format_datetime(suite.created_time),
            updated_time=format_datetime(suite.updated_time),
            case_count=case_count,
            cases=None
        )
        
        return ResponseSchema.success(data=suite_data, msg="更新成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.delete("/{suite_id}", summary="删除测试套件")
async def delete_test_suite(suite_id: int, force: bool = Query(False)):
    """
    删除测试套件
    """
    try:
        suite = await TestUICaseSuite.get_or_none(id=suite_id)
        
        if not suite:
            return ResponseSchema.error(msg="测试套件不存在", code=404)
        
        # 检查是否被测试单引用
        task_count = await TestUITaskContent.filter(
            item_type='SUITE',
            item_id=suite_id
        ).count()
        
        if task_count > 0 and not force:
            return ResponseSchema.error(
                msg=f"该套件已被{task_count}个测试单使用，请先解除关联或使用强制删除",
                code=400
            )
        
        if force:
            await TestUITaskContent.filter(item_type='SUITE', item_id=suite_id).delete()
        
        # 删除用例关联
        await TestUICasesSuitesRelation.filter(test_suite_id=suite_id).delete()
        
        # 删除套件
        await suite.delete()
        
        return ResponseSchema.success(msg="删除成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/{suite_id}/preview", summary="预览匹配用例")
async def preview_matched_cases(suite_id: int, filter_conditions: dict):
    """
    根据筛选条件预览匹配的用例
    """
    try:
        # 不要硬编码状态过滤，让用户自己选择
        query = TestUICase.all()
        
        # 应用筛选条件
        if filter_conditions.get('module'):
            query = query.filter(module__in=filter_conditions['module'])
        if filter_conditions.get('priority'):
            query = query.filter(priority__in=filter_conditions['priority'])
        if filter_conditions.get('status'):
            query = query.filter(status__in=filter_conditions['status'])
        if filter_conditions.get('created_by'):
            query = query.filter(created_by__in=filter_conditions['created_by'])
        
        # 获取所有符合条件的用例
        cases = await query.all()
        
        # 如果有标签筛选，在Python中过滤
        if filter_conditions.get('tags'):
            filter_tags = set(filter_conditions['tags'])
            filtered_cases = []
            for case in cases:
                if case.tags and isinstance(case.tags, list):
                    case_tags = set(case.tags)
                    # 检查是否有交集
                    if filter_tags & case_tags:
                        filtered_cases.append(case)
            cases = filtered_cases
        
        matched_count = len(cases)
        
        case_list = [
            {
                "id": case.id,
                "name": case.name,
                "priority": case.priority,
                "module": case.module,
                "product": case.product,
                "tags": case.tags,
                "status": case.status
            }
            for case in cases
        ]
        
        return ResponseSchema.success(data={
            "matched_count": matched_count,
            "cases": case_list
        })
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/{suite_id}/cases", summary="获取套件用例")
async def get_suite_cases(suite_id: int):
    """
    获取套件关联的用例列表
    """
    try:
        suite = await TestUICaseSuite.get_or_none(id=suite_id)
        
        if not suite:
            return ResponseSchema.error(msg="测试套件不存在", code=404)
        
        relations = await TestUICasesSuitesRelation.filter(
            test_suite_id=suite_id
        ).prefetch_related('test_case').order_by('sort_order').all()
        
        cases = [
            {
                "id": rel.test_case.id,
                "name": rel.test_case.name,
                "priority": rel.test_case.priority,
                "product": rel.test_case.product,
                "status": rel.test_case.status,
                "sort_order": rel.sort_order
            }
            for rel in relations
        ]
        
        return ResponseSchema.success(data=cases)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/{suite_id}/cases", summary="添加用例到套件")
async def add_cases_to_suite(suite_id: int, case_ids: List[int]):
    """
    添加用例到套件
    """
    try:
        suite = await TestUICaseSuite.get_or_none(id=suite_id)
        
        if not suite:
            return ResponseSchema.error(msg="测试套件不存在", code=404)
        
        # 获取当前max sort_order
        max_sort = await TestUICasesSuitesRelation.filter(test_suite_id=suite_id).count()
        
        added_count = 0
        for case_id in case_ids:
            # 检查是否已存在
            exists = await TestUICasesSuitesRelation.filter(
                test_suite_id=suite_id,
                test_case_id=case_id
            ).exists()
            
            if not exists:
                await TestUICasesSuitesRelation.create(
                    test_suite_id=suite_id,
                    test_case_id=case_id,
                    sort_order=max_sort + added_count + 1
                )
                added_count += 1
        
        return ResponseSchema.success(
            data={"added_count": added_count},
            msg=f"成功添加{added_count}个用例"
        )
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.delete("/{suite_id}/cases/{case_id}", summary="从套件移除用例")
async def remove_case_from_suite(suite_id: int, case_id: int):
    """
    从套件中移除用例
    """
    try:
        relation = await TestUICasesSuitesRelation.get_or_none(
            test_suite_id=suite_id,
            test_case_id=case_id
        )
        
        if not relation:
            return ResponseSchema.error(msg="用例关联不存在", code=404)
        
        await relation.delete()
        
        return ResponseSchema.success(msg="移除成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/{suite_id}/cases/reorder", summary="调整用例顺序")
async def reorder_suite_cases(suite_id: int, case_ids: List[int]):
    """
    调整套件中用例的执行顺序
    """
    try:
        for index, case_id in enumerate(case_ids):
            relation = await TestUICasesSuitesRelation.get_or_none(
                test_suite_id=suite_id,
                test_case_id=case_id
            )
            if relation:
                relation.sort_order = index + 1
                await relation.save()
        
        return ResponseSchema.success(msg="顺序调整成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/{suite_id}/sync", summary="同步筛选条件")
async def sync_suite_cases(suite_id: int):
    """
    根据筛选条件同步套件用例
    """
    try:
        suite = await TestUICaseSuite.get_or_none(id=suite_id)
        
        if not suite:
            return ResponseSchema.error(msg="测试套件不存在", code=404)
        
        # 清空现有用例
        await TestUICasesSuitesRelation.filter(test_suite_id=suite_id).delete()
        
        # 根据筛选条件查询用例
        query = TestUICase.all()
        filter_conditions = suite.filter_conditions or {}
        
        if filter_conditions.get('module'):
            query = query.filter(module__in=filter_conditions['module'])
        if filter_conditions.get('priority'):
            query = query.filter(priority__in=filter_conditions['priority'])
        if filter_conditions.get('status'):
            query = query.filter(status__in=filter_conditions['status'])
        if filter_conditions.get('created_by'):
            query = query.filter(created_by__in=filter_conditions['created_by'])
        
        cases = await query.all()
        
        # 如果有标签筛选，在Python中过滤
        if filter_conditions.get('tags'):
            filter_tags = set(filter_conditions['tags'])
            filtered_cases = []
            for case in cases:
                if case.tags and isinstance(case.tags, list):
                    case_tags = set(case.tags)
                    if filter_tags & case_tags:
                        filtered_cases.append(case)
            cases = filtered_cases
        
        # 添加用例
        for index, case in enumerate(cases):
            await TestUICasesSuitesRelation.create(
                test_suite_id=suite_id,
                test_case_id=case.id,
                sort_order=index + 1
            )
        
        return ResponseSchema.success(
            data={"synced_count": len(cases)},
            msg=f"同步成功，共{len(cases)}个用例"
        )
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)
