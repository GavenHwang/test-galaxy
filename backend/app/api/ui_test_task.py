"""
UI测试单管理API
"""
from fastapi import APIRouter, Query, Request
from typing import List, Optional
from app.schemas.response import ResponseSchema
from app.schemas.ui_test import (
    TestTaskCreateSchema,
    TestTaskUpdateSchema,
    TestTaskResponseSchema
)
from app.models.ui_test import (
    TestUITask,
    TestUITaskContent,
    TestUIReport,
    TestUICaseSuite,
    TestUICase,
    TaskStatus
)

router = APIRouter()


@router.post("", summary="创建测试单", response_model=ResponseSchema[TestTaskResponseSchema])
async def create_test_task(data: TestTaskCreateSchema, request: Request):
    """
    创建测试单
    """
    try:
        current_user = request.state.current_user
        created_by = current_user.get("username", "system") if current_user else "system"
        
        task = await TestUITask.create(
            name=data.name,
            description=data.description,
            environment=data.environment,
            status=TaskStatus.PENDING,
            execute_config=data.execute_config or {},
            created_by=created_by
        )
        
        task_data = TestTaskResponseSchema(
            id=task.id,
            name=task.name,
            description=task.description,
            environment=task.environment,
            status=task.status,
            execute_config=task.execute_config,
            created_by=task.created_by,
            created_time=task.created_time,
            updated_time=task.updated_time,
            start_time=task.start_time,
            end_time=task.end_time,
            total_cases=0,
            executed_cases=0,
            passed_cases=0,
            failed_cases=0,
            progress=0.0
        )
        
        return ResponseSchema.success(data=task_data, msg="创建成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("", summary="获取测试单列表")
async def get_test_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    created_by: Optional[str] = Query(None)
):
    """
    分页获取测试单列表
    """
    try:
        query = TestUITask.all()
        
        if name:
            query = query.filter(name__icontains=name)
        if status:
            query = query.filter(status=status)
        if environment:
            query = query.filter(environment=environment)
        if created_by:
            query = query.filter(created_by=created_by)
        
        total = await query.count()
        offset = (page - 1) * page_size
        tasks = await query.offset(offset).limit(page_size).order_by('-created_time')
        
        task_list = []
        for task in tasks:
            # 计算用例总数
            total_cases = 0
            contents = await TestUITaskContent.filter(task_id=task.id).all()
            for content in contents:
                if content.item_type == 'SUITE':
                    count = await TestUICaseSuite.get(id=content.item_id).prefetch_related('cases').count()
                    total_cases += count
                else:
                    total_cases += 1
            
            task_data = TestTaskResponseSchema(
                id=task.id,
                name=task.name,
                description=task.description,
                environment=task.environment,
                status=task.status,
                execute_config=task.execute_config,
                created_by=task.created_by,
                created_time=task.created_time,
                updated_time=task.updated_time,
                start_time=task.start_time,
                end_time=task.end_time,
                total_cases=total_cases,
                executed_cases=task.executed_cases or 0,
                passed_cases=task.passed_cases or 0,
                failed_cases=task.failed_cases or 0,
                progress=task.progress or 0.0
            )
            task_list.append(task_data)
        
        result = {
            "items": task_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
        
        return ResponseSchema.success(data=result)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/{task_id}", summary="获取测试单详情")
async def get_test_task(task_id: int):
    """
    获取测试单详细信息
    """
    try:
        task = await TestUITask.get_or_none(id=task_id)
        
        if not task:
            return ResponseSchema.error(msg="测试单不存在", code=404)
        
        # 计算用例总数
        total_cases = 0
        contents = await TestUITaskContent.filter(task_id=task.id).all()
        for content in contents:
            if content.item_type == 'SUITE':
                suite = await TestUICaseSuite.get_or_none(id=content.item_id)
                if suite:
                    count = await suite.cases.all().count()
                    total_cases += count
            else:
                total_cases += 1
        
        task_data = TestTaskResponseSchema(
            id=task.id,
            name=task.name,
            description=task.description,
            environment=task.environment,
            status=task.status,
            execute_config=task.execute_config,
            created_by=task.created_by,
            created_time=task.created_time,
            updated_time=task.updated_time,
            start_time=task.start_time,
            end_time=task.end_time,
            total_cases=total_cases,
            executed_cases=task.executed_cases or 0,
            passed_cases=task.passed_cases or 0,
            failed_cases=task.failed_cases or 0,
            progress=task.progress or 0.0
        )
        
        return ResponseSchema.success(data=task_data)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.put("/{task_id}", summary="更新测试单")
async def update_test_task(task_id: int, data: TestTaskUpdateSchema):
    """
    更新测试单信息
    """
    try:
        task = await TestUITask.get_or_none(id=task_id)
        
        if not task:
            return ResponseSchema.error(msg="测试单不存在", code=404)
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        await task.save()
        
        return ResponseSchema.success(msg="更新成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.delete("/{task_id}", summary="删除测试单")
async def delete_test_task(task_id: int):
    """
    删除测试单
    """
    try:
        task = await TestUITask.get_or_none(id=task_id)
        
        if not task:
            return ResponseSchema.error(msg="测试单不存在", code=404)
        
        # 删除内容
        await TestUITaskContent.filter(task_id=task_id).delete()
        
        # 删除测试单
        await task.delete()
        
        return ResponseSchema.success(msg="删除成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/{task_id}/execute", summary="执行测试单")
async def execute_test_task(task_id: int):
    """
    立即执行测试单
    """
    try:
        task = await TestUITask.get_or_none(id=task_id)
        
        if not task:
            return ResponseSchema.error(msg="测试单不存在", code=404)
        
        # 更新状态为执行中
        task.status = TaskStatus.RUNNING
        await task.save()
        
        # TODO: 调用执行引擎执行测试
        # 这里应该启动后台任务执行测试用例
        
        return ResponseSchema.success(msg="测试单已开始执行")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/{task_id}/cancel", summary="取消执行")
async def cancel_test_task(task_id: int):
    """
    取消正在执行的测试单
    """
    try:
        task = await TestUITask.get_or_none(id=task_id)
        
        if not task:
            return ResponseSchema.error(msg="测试单不存在", code=404)
        
        if task.status != TaskStatus.RUNNING:
            return ResponseSchema.error(msg="测试单未在执行中", code=400)
        
        task.status = TaskStatus.CANCELLED
        await task.save()
        
        return ResponseSchema.success(msg="已取消执行")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/{task_id}/progress", summary="获取执行进度")
async def get_task_progress(task_id: int):
    """
    获取测试单执行进度
    """
    try:
        task = await TestUITask.get_or_none(id=task_id)
        
        if not task:
            return ResponseSchema.error(msg="测试单不存在", code=404)
        
        progress_data = {
            "status": task.status,
            "total_cases": task.total_cases or 0,
            "executed_cases": task.executed_cases or 0,
            "passed_cases": task.passed_cases or 0,
            "failed_cases": task.failed_cases or 0,
            "skipped_cases": 0,
            "progress": task.progress or 0.0,
            "start_time": task.start_time,
            "elapsed_time": None,
            "estimated_total_time": None,
            "remaining_time": None
        }
        
        return ResponseSchema.success(data=progress_data)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/{task_id}/contents", summary="获取测试内容")
async def get_task_contents(task_id: int):
    """
    获取测试单的测试内容（套件和用例）
    """
    try:
        task = await TestUITask.get_or_none(id=task_id)
        
        if not task:
            return ResponseSchema.error(msg="测试单不存在", code=404)
        
        contents = await TestUITaskContent.filter(task_id=task_id).order_by('sort_order').all()
        
        content_list = []
        for content in contents:
            item_data = {
                "id": content.id,
                "item_type": content.item_type,
                "item_id": content.item_id,
                "sort_order": content.sort_order
            }
            
            if content.item_type == 'SUITE':
                suite = await TestUICaseSuite.get_or_none(id=content.item_id)
                if suite:
                    item_data["name"] = suite.name
            else:
                case = await TestUICase.get_or_none(id=content.item_id)
                if case:
                    item_data["name"] = case.name
            
            content_list.append(item_data)
        
        return ResponseSchema.success(data=content_list)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/{task_id}/contents", summary="添加测试内容")
async def add_task_content(task_id: int, item_type: str, item_id: int):
    """
    添加测试内容到测试单
    """
    try:
        task = await TestUITask.get_or_none(id=task_id)
        
        if not task:
            return ResponseSchema.error(msg="测试单不存在", code=404)
        
        # 获取当前最大sort_order
        max_sort = await TestUITaskContent.filter(task_id=task_id).count()
        
        await TestUITaskContent.create(
            task_id=task_id,
            item_type=item_type,
            item_id=item_id,
            sort_order=max_sort + 1
        )
        
        return ResponseSchema.success(msg="添加成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.delete("/{task_id}/contents/{content_id}", summary="移除测试内容")
async def remove_task_content(task_id: int, content_id: int):
    """
    从测试单移除测试内容
    """
    try:
        content = await TestUITaskContent.get_or_none(id=content_id, task_id=task_id)
        
        if not content:
            return ResponseSchema.error(msg="测试内容不存在", code=404)
        
        await content.delete()
        
        return ResponseSchema.success(msg="移除成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/{task_id}/contents/reorder", summary="调整执行顺序")
async def reorder_task_contents(task_id: int, content_ids: List[int]):
    """
    调整测试内容的执行顺序
    """
    try:
        for index, content_id in enumerate(content_ids):
            content = await TestUITaskContent.get_or_none(id=content_id, task_id=task_id)
            if content:
                content.sort_order = index + 1
                await content.save()
        
        return ResponseSchema.success(msg="顺序调整成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/{task_id}/reports", summary="获取执行报告列表")
async def get_task_reports(task_id: int):
    """
    获取测试单的执行报告列表
    """
    try:
        task = await TestUITask.get_or_none(id=task_id)
        
        if not task:
            return ResponseSchema.error(msg="测试单不存在", code=404)
        
        reports = await TestUIReport.filter(test_task_id=task_id).order_by('-created_time').all()
        
        report_list = [
            {
                "id": report.id,
                "test_task_id": report.test_task_id,
                "total_cases": report.total_cases,
                "passed_cases": report.passed_cases,
                "failed_cases": report.failed_cases,
                "skipped_cases": report.skipped_cases,
                "pass_rate": report.pass_rate,
                "start_time": report.start_time,
                "end_time": report.end_time,
                "duration": report.duration,
                "created_time": report.created_time
            }
            for report in reports
        ]
        
        return ResponseSchema.success(data=report_list)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)
