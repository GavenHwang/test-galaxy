"""
结果收集器
负责收集执行日志并写入数据库
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List

from app.models.ui_test import (
    TestUIReport,
    TestUICaseExecutionRecord,
    TestUICaseStepExecutionRecord,
    TestUIStep,
    ExecutionStatus
)
from app.log import logger


class ResultCollector:
    """
    结果收集器
    负责收集执行日志并写入数据库
    """
    
    async def collect_results(self, work_dir: Path, report_id: int):
        """
        收集所有用例的执行结果
        
        Args:
            work_dir: 工作目录
            report_id: 测试报告ID
        """
        logs_dir = work_dir / 'logs'
        if not logs_dir.exists():
            logger.warning(f"日志目录不存在: {logs_dir}")
            return
        
        # 遍历所有日志文件
        for log_file in logs_dir.glob('case_*.json'):
            try:
                await self._process_log_file(log_file, report_id)
            except Exception as e:
                logger.error(f"处理日志文件失败 {log_file}: {e}")
    
    async def _process_log_file(self, log_file: Path, report_id: int):
        """处理单个日志文件"""
        try:
            # 1. 读取日志文件
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            case_info = log_data['case_info']
            execution_info = log_data['execution_info']
            steps = log_data['steps']
            
            # 2. 创建用例执行记录
            case_record = await TestUICaseExecutionRecord.create(
                test_case_id=case_info['case_id'],
                test_report_id=report_id,
                status=execution_info['status'],
                start_time=datetime.strptime(execution_info['start_time'], '%Y-%m-%d %H:%M:%S'),
                end_time=datetime.strptime(execution_info['end_time'], '%Y-%m-%d %H:%M:%S'),
                duration=execution_info['duration'],
                error_message=execution_info.get('error_message')
            )
            
            # 3. 创建步骤执行记录
            for step_data in steps:
                # 查询步骤定义获取 element_id
                step_def = await TestUIStep.filter(
                    test_case_id=case_info['case_id'],
                    step_number=step_data['step_number']
                ).first()
                
                await TestUICaseStepExecutionRecord.create(
                    case_execution_record_id=case_record.id,
                    step_number=step_data['step_number'],
                    action=step_data['action'],
                    description=step_data.get('description'),  # 保存步骤描述
                    element_id=step_def.element_id if step_def else None,
                    input_data=step_def.input_data if step_def else None,
                    status=step_data['status'],
                    start_time=datetime.strptime(step_data['start_time'], '%Y-%m-%d %H:%M:%S'),
                    end_time=datetime.strptime(step_data['end_time'], '%Y-%m-%d %H:%M:%S'),
                    duration=step_data['duration'],
                    error_message=step_data.get('error_message'),
                    screenshot_path=step_data.get('screenshot_path')
                )
            
            logger.info(f"处理日志文件成功: {log_file.name}")
            
        except Exception as e:
            logger.error(f"处理日志文件异常 {log_file}: {e}")
            raise
