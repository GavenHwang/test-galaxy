"""
UI测试报告管理API
"""
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime
from app.schemas.response import ResponseSchema
from app.models.ui_test import (
    TestUIReport,
    TestUICaseExecutionRecord,
    TestUICaseStepExecutionRecord,
    TestUITask
)

router = APIRouter()


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """格式化时间为 YYYY-MM-DD HH:MM:SS 格式"""
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')


@router.get("", summary="获取测试报告列表")
async def get_test_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    test_task_id: Optional[int] = Query(None)
):
    """
    分页获取测试报告列表
    """
    try:
        query = TestUIReport.all()
        
        if test_task_id:
            query = query.filter(test_task_id=test_task_id)
        
        total = await query.count()
        offset = (page - 1) * page_size
        reports = await query.offset(offset).limit(page_size).order_by('-created_time')
        
        report_list = [
            {
                "id": report.id,
                "test_task_id": report.test_task_id,
                "execution_time": format_datetime(report.execution_time),
                "total_cases": report.total_cases,
                "passed_cases": report.passed_cases,
                "failed_cases": report.failed_cases,
                "skipped_cases": report.skipped_cases,
                "pass_rate": float(report.pass_rate),
                "execution_duration": report.execution_duration,
                "report_data": report.report_data,
                "created_time": format_datetime(report.created_time),
                "updated_time": format_datetime(report.updated_time)
            }
            for report in reports
        ]
        
        result = {
            "items": report_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
        
        return ResponseSchema.success(data=result)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/{report_id}", summary="获取测试报告详情")
async def get_test_report(report_id: int):
    """
    获取测试报告详细信息
    """
    try:
        report = await TestUIReport.get_or_none(id=report_id)
        
        if not report:
            return ResponseSchema.error(msg="测试报告不存在", code=404)
        
        # 获取测试单信息
        task = await TestUITask.get_or_none(id=report.test_task_id)
        task_name = task.name if task else "未知"
        task_start_time = task.start_time if task else None
        task_end_time = task.end_time if task else None
        
        # 查询用例执行记录
        case_records = await TestUICaseExecutionRecord.filter(
            test_report_id=report_id
        ).all()
        
        case_list = []
        for record in case_records:
            # 查询步骤执行记录
            step_records = await TestUICaseStepExecutionRecord.filter(
                case_execution_record_id=record.id
            ).order_by('step_number').all()
            
            steps = []
            for step in step_records:
                # 直接使用步骤记录中的 description 字段
                description = step.description or step.action
                
                steps.append({
                    "step_number": step.step_number,
                    "action": step.action,
                    "description": description,
                    "input_data": step.input_data,
                    "status": step.status,
                    "start_time": format_datetime(step.start_time),
                    "end_time": format_datetime(step.end_time),
                    "duration": step.duration,
                    "error_message": step.error_message,
                    "screenshot_path": step.screenshot_path
                })
            
            case_list.append({
                "test_case_id": record.test_case_id,
                "status": record.status,
                "start_time": format_datetime(record.start_time),
                "end_time": format_datetime(record.end_time),
                "duration": record.duration,
                "error_message": record.error_message,
                "screenshot_path": record.screenshot_path,
                "steps": steps
            })
        
        report_data = {
            "id": report.id,
            "test_task_id": report.test_task_id,
            "test_task_name": task_name,
            "start_time": format_datetime(task_start_time),
            "end_time": format_datetime(task_end_time),
            "execution_time": format_datetime(report.execution_time),
            "total_cases": report.total_cases,
            "passed_cases": report.passed_cases,
            "failed_cases": report.failed_cases,
            "skipped_cases": report.skipped_cases,
            "pass_rate": float(report.pass_rate),
            "execution_duration": report.execution_duration,
            "report_data": report.report_data,
            "created_time": format_datetime(report.created_time),
            "updated_time": format_datetime(report.updated_time),
            "cases": case_list
        }
        
        return ResponseSchema.success(data=report_data)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/{report_id}/summary", summary="获取报告摘要")
async def get_report_summary(report_id: int):
    """
    获取测试报告摘要信息
    """
    try:
        report = await TestUIReport.get_or_none(id=report_id)
        
        if not report:
            return ResponseSchema.error(msg="测试报告不存在", code=404)
        
        summary = {
            "total_cases": report.total_cases,
            "passed_cases": report.passed_cases,
            "failed_cases": report.failed_cases,
            "skipped_cases": report.skipped_cases,
            "pass_rate": float(report.pass_rate),
            "execution_duration": report.execution_duration,
            "execution_time": format_datetime(report.execution_time)
        }
        
        return ResponseSchema.success(data=summary)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/compare", summary="对比多个报告")
async def compare_reports(report_ids: str = Query(..., description="报告ID列表，逗号分隔")):
    """
    对比多个测试报告
    """
    try:
        ids = [int(id.strip()) for id in report_ids.split(',')]
        
        reports = await TestUIReport.filter(id__in=ids).all()
        
        if len(reports) != len(ids):
            return ResponseSchema.error(msg="部分报告不存在", code=404)
        
        compare_data = {
            "reports": [
                {
                    "id": report.id,
                    "test_task_id": report.test_task_id,
                    "execution_time": format_datetime(report.execution_time),
                    "total_cases": report.total_cases,
                    "passed_cases": report.passed_cases,
                    "failed_cases": report.failed_cases,
                    "pass_rate": float(report.pass_rate),
                    "execution_duration": report.execution_duration,
                    "created_time": format_datetime(report.created_time)
                }
                for report in reports
            ]
        }
        
        return ResponseSchema.success(data=compare_data)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.delete("/{report_id}", summary="删除测试报告")
async def delete_test_report(report_id: int):
    """
    删除测试报告（级联删除相关的用例执行记录和步骤记录）
    """
    try:
        report = await TestUIReport.get_or_none(id=report_id)
        
        if not report:
            return ResponseSchema.error(msg="测试报告不存在", code=404)
        
        # 删除报告（模型中设置了级联删除，会自动删除相关记录）
        await report.delete()
        
        return ResponseSchema.success(msg="删除成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)
