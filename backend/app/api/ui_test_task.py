"""
UI测试单管理API
"""
from fastapi import APIRouter, Query, Request
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
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
    TestUICasesSuitesRelation,
    TestUICase,
    TestUICaseExecutionRecord,
    TaskStatus
)

router = APIRouter()


def format_datetime(dt: datetime) -> str:
    """格式化时间为 YYYY-MM-DD HH:MM:SS 格式"""
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')


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
            product=data.product,
            environment=data.environment,
            status=TaskStatus.PENDING,
            execute_config=data.execute_config or {},
            created_by=created_by
        )
        
        # 保存选择的套件
        if data.suites:
            for suite_id in data.suites:
                await TestUITaskContent.create(
                    test_task_id=task.id,
                    item_type='SUITE',
                    item_id=suite_id,
                    sort_order=0
                )
        
        # 保存选择的用例
        if data.cases:
            for case_id in data.cases:
                await TestUITaskContent.create(
                    test_task_id=task.id,
                    item_type='CASE',
                    item_id=case_id,
                    sort_order=0
                )
        
        task_data = TestTaskResponseSchema(
            id=task.id,
            name=task.name,
            description=task.description,
            product=task.product,
            environment=task.environment,
            status=task.status,
            execute_config=task.execute_config,
            created_by=task.created_by,
            created_time=format_datetime(task.created_time),
            updated_time=format_datetime(task.updated_time),
            start_time=format_datetime(task.start_time),
            end_time=format_datetime(task.end_time),
            total_cases=len(data.cases or []),
            executed_cases=0,
            passed_cases=0,
            failed_cases=0,
            progress=0.0,
            suites=data.suites or [],
            cases=data.cases or []
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
            contents = await TestUITaskContent.filter(test_task_id=task.id).all()
            for content in contents:
                if content.item_type == 'SUITE':
                    suite = await TestUICaseSuite.get_or_none(id=content.item_id)
                    if suite:
                        # 通过case_relations查询套件包含的用例数
                        count = await TestUICasesSuitesRelation.filter(test_suite_id=content.item_id).count()
                        total_cases += count
                else:
                    total_cases += 1
            
            task_data = TestTaskResponseSchema(
                id=task.id,
                name=task.name,
                description=task.description,
                product=task.product,
                environment=task.environment,
                status=task.status,
                execute_config=task.execute_config,
                created_by=task.created_by,
                created_time=format_datetime(task.created_time),
                updated_time=format_datetime(task.updated_time),
                start_time=format_datetime(task.start_time),
                end_time=format_datetime(task.end_time),
                total_cases=total_cases,
                executed_cases=task.executed_cases or 0,
                passed_cases=task.passed_cases or 0,
                failed_cases=task.failed_cases or 0,
                progress=float(task.progress or 0.0)
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
        
        # 获取已选择的套件和用例ID
        contents = await TestUITaskContent.filter(test_task_id=task.id).all()
        selected_suites = []
        selected_cases = []
        total_cases = 0
        
        for content in contents:
            if content.item_type == 'SUITE':
                selected_suites.append(content.item_id)
                # 通过case_relations查询套件包含的用例数
                count = await TestUICasesSuitesRelation.filter(test_suite_id=content.item_id).count()
                total_cases += count
            else:
                selected_cases.append(content.item_id)
                total_cases += 1
        
        task_data = TestTaskResponseSchema(
            id=task.id,
            name=task.name,
            description=task.description,
            product=task.product,
            environment=task.environment,
            status=task.status,
            execute_config=task.execute_config,
            created_by=task.created_by,
            created_time=format_datetime(task.created_time),
            updated_time=format_datetime(task.updated_time),
            start_time=format_datetime(task.start_time),
            end_time=format_datetime(task.end_time),
            total_cases=total_cases,
            executed_cases=task.executed_cases or 0,
            passed_cases=task.passed_cases or 0,
            failed_cases=task.failed_cases or 0,
            progress=float(task.progress or 0.0),
            suites=selected_suites,
            cases=selected_cases
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
        
        # 处理套件和用例更新
        suites = update_data.pop('suites', None)
        cases = update_data.pop('cases', None)
        
        # 更新基本信息
        for field, value in update_data.items():
            setattr(task, field, value)
        
        await task.save()
        
        # 如果提供了套件或用例，则更新测试内容
        if suites is not None or cases is not None:
            # 删除现有内容
            await TestUITaskContent.filter(test_task_id=task_id).delete()
            
            # 添加套件
            if suites:
                for suite_id in suites:
                    await TestUITaskContent.create(
                        test_task_id=task_id,
                        item_type='SUITE',
                        item_id=suite_id,
                        sort_order=0
                    )
            
            # 添加用例
            if cases:
                for case_id in cases:
                    await TestUITaskContent.create(
                        test_task_id=task_id,
                        item_type='CASE',
                        item_id=case_id,
                        sort_order=0
                    )
        
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
        await TestUITaskContent.filter(test_task_id=task_id).delete()
        
        # 删除测试单
        await task.delete()
        
        return ResponseSchema.success(msg="删除成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/{task_id}/execute", summary="执行测试单")
async def execute_test_task(task_id: int, request: Request):
    """
    立即执行测试单
    """
    try:
        from app.core.task_execution_scheduler import TaskExecutionScheduler
        import asyncio
        
        task = await TestUITask.get_or_none(id=task_id)
        
        if not task:
            return ResponseSchema.error(msg="测试单不存在", code=404)
        
        # 检查状态
        if task.status == TaskStatus.RUNNING:
            return ResponseSchema.error(msg="测试单正在执行中", code=400)
        
        # 更新状态为执行中
        task.status = TaskStatus.RUNNING
        task.start_time = datetime.now()
        await task.save()
        
        # 创建执行调度器
        scheduler = TaskExecutionScheduler()
        
        # 在后台执行（不阻塞 API 响应）
        asyncio.create_task(scheduler.execute_task(task_id))
        
        return ResponseSchema.success(
            msg="测试单已开始执行",
            data={
                "task_id": task_id,
                "status": task.status,
                "start_time": format_datetime(task.start_time)
            }
        )
        
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
        
        if task.status not in [TaskStatus.RUNNING, TaskStatus.PAUSED]:
            return ResponseSchema.error(msg="测试单未在执行中", code=400)
        
        task.status = TaskStatus.CANCELLED
        task.end_time = datetime.now()
        await task.save()
        
        return ResponseSchema.success(msg="已取消执行")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/{task_id}/pause", summary="暂停执行")
async def pause_test_task(task_id: int):
    """
    暂停正在执行的测试单
    """
    try:
        task = await TestUITask.get_or_none(id=task_id)
        
        if not task:
            return ResponseSchema.error(msg="测试单不存在", code=404)
        
        if task.status != TaskStatus.RUNNING:
            return ResponseSchema.error(msg="测试单未在执行中", code=400)
        
        task.status = TaskStatus.PAUSED
        await task.save()
        
        return ResponseSchema.success(msg="已暂停执行")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/{task_id}/resume", summary="继续执行")
async def resume_test_task(task_id: int):
    """
    继续执行已暂停的测试单
    """
    try:
        from app.core.task_execution_scheduler import TaskExecutionScheduler
        import asyncio
        
        task = await TestUITask.get_or_none(id=task_id)
        
        if not task:
            return ResponseSchema.error(msg="测试单不存在", code=404)
        
        if task.status != TaskStatus.PAUSED:
            return ResponseSchema.error(msg="测试单未处于暂停状态", code=400)
        
        # 更新状态为执行中
        task.status = TaskStatus.RUNNING
        await task.save()
        
        # 创建执行调度器
        scheduler = TaskExecutionScheduler()
        
        # 在后台继续执行（不阻塞 API 响应）
        asyncio.create_task(scheduler.execute_task(task_id))
        
        return ResponseSchema.success(
            msg="已继续执行",
            data={
                "task_id": task_id,
                "status": task.status
            }
        )
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/{task_id}/restart", summary="重新执行")
async def restart_test_task(task_id: int):
    """
    重新执行测试单（清理已有结果，从头开始）
    """
    try:
        from app.core.task_execution_scheduler import TaskExecutionScheduler
        import asyncio
        
        task = await TestUITask.get_or_none(id=task_id)
        
        if not task:
            return ResponseSchema.error(msg="测试单不存在", code=404)
        
        # 清理已有执行记录（如果需要保留历史，可以改为标记而不是删除）
        # 这里我们删除该测试单的所有执行记录
        reports = await TestUIReport.filter(test_task=task_id).all()
        for report in reports:
            # 删除报告的用例执行记录
            await TestUICaseExecutionRecord.filter(test_report_id=report.id).delete()
            # 删除报告
            await report.delete()
        
        # 重置任务状态和统计
        task.status = TaskStatus.RUNNING
        task.start_time = datetime.now()
        # end_time 设置为 null 需要直接更新数据库
        task.executed_cases = 0
        task.passed_cases = 0
        task.failed_cases = 0
        task.progress = Decimal('0.0')
        await task.save(update_fields=['status', 'start_time', 'executed_cases', 'passed_cases', 'failed_cases', 'progress'])
        
        # 创建执行调度器
        scheduler = TaskExecutionScheduler()
        
        # 在后台执行（不阻塞 API 响应）
        asyncio.create_task(scheduler.execute_task(task_id))
        
        return ResponseSchema.success(
            msg="测试单已开始重新执行",
            data={
                "task_id": task_id,
                "status": task.status,
                "start_time": format_datetime(task.start_time)
            }
        )
        
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


@router.get("/{task_id}/log", summary="获取执行日志")
async def get_task_log(task_id: int, offset: int = 0):
    """
    获取测试单执行日志（支持增量读取）
    
    参数:
    - task_id: 测试单ID
    - offset: 读取偏移量（字节），默认为0表示从头读取
    
    返回:
    - log_content: 日志内容
    - next_offset: 下次读取的偏移量
    - is_complete: 任务是否已完成
    """
    try:
        task = await TestUITask.get_or_none(id=task_id)
        
        if not task:
            return ResponseSchema.error(msg="测试单不存在", code=404)
        
        log_content = ""
        next_offset = offset
        
        # 如果有日志文件路径，读取文件内容
        if task.log_file_path:
            import os
            if os.path.exists(task.log_file_path):
                try:
                    with open(task.log_file_path, 'r', encoding='utf-8') as f:
                        # 移动到offset位置
                        f.seek(offset)
                        # 读取新内容
                        log_content = f.read()
                        # 获取当前文件位置作为下次的offset
                        next_offset = f.tell()
                except Exception as e:
                    return ResponseSchema.error(msg=f"读取日志文件失败: {str(e)}", code=500)
            else:
                return ResponseSchema.error(msg="日志文件不存在，测试可能未开始执行或执行异常", code=404)
        else:
            return ResponseSchema.error(msg="暂无执行日志，测试尚未开始", code=404)
        
        # 判断任务是否已完成
        is_complete = task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
        
        log_data = {
            "task_id": task_id,
            "task_name": task.name,
            "status": task.status,
            "log_content": log_content,
            "next_offset": next_offset,
            "is_complete": is_complete,
            "start_time": format_datetime(task.start_time) if task.start_time else None,
            "end_time": format_datetime(task.end_time) if task.end_time else None
        }
        
        return ResponseSchema.success(data=log_data)
        
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
        
        contents = await TestUITaskContent.filter(test_task_id=task_id).order_by('sort_order').all()
        
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
        max_sort = await TestUITaskContent.filter(test_task_id=task_id).count()
        
        await TestUITaskContent.create(
            test_task_id=task_id,
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
        content = await TestUITaskContent.get_or_none(id=content_id, test_task_id=task_id)
        
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
            content = await TestUITaskContent.get_or_none(id=content_id, test_task_id=task_id)
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
        
        reports = await TestUIReport.filter(test_task=task_id).order_by('-created_time').all()
        
        report_list = [
            {
                "id": report.id,
                "test_task_id": task_id,
                "total_cases": report.total_cases,
                "passed_cases": report.passed_cases,
                "failed_cases": report.failed_cases,
                "skipped_cases": report.skipped_cases,
                "pass_rate": float(report.pass_rate),
                "start_time": format_datetime(report.execution_time),
                "end_time": format_datetime(report.created_time),
                "duration": report.execution_duration,
                "created_time": format_datetime(report.created_time)
            }
            for report in reports
        ]
        
        return ResponseSchema.success(data=report_list)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)
