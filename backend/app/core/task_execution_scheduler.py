"""
测试单执行调度器
负责协调整个测试单的执行流程
"""
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from decimal import Decimal

from app.models.ui_test import (
    TestUITask,
    TestUIReport,
    TestUITaskContent,
    TestUICasesSuitesRelation,
    TaskStatus,
    TaskContentType
)
from app.core.config_generator import ConfigGenerator
from app.core.script_generator import ScriptGenerator
from app.core.result_collector import ResultCollector
from app.core.case_executor import CaseExecutor
from app.log import logger


class TaskExecutionScheduler:
    """
    测试单执行调度器
    负责协调整个测试单的执行流程
    """
    
    def __init__(self):
        self.config_gen = ConfigGenerator()
        self.script_gen = ScriptGenerator()
        self.result_collector = ResultCollector()
        self.case_executor = CaseExecutor()
        self.log_file_path = None  # 日志文件路径
    
    def _add_log(self, message: str, level: str = "INFO"):
        """添加日志并写入文件"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # 写入日志文件
        if self.log_file_path:
            try:
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
                    f.flush()  # 立即刷新到磁盘
            except Exception as e:
                logger.error(f"写入日志文件失败: {e}")
        
        logger.info(message)
    
    def _create_log_file(self, work_dir: Path) -> str:
        """创建日志文件"""
        log_dir = work_dir / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / 'execution.log'
        self.log_file_path = str(log_file)
        
        # 创建日志文件并写入头部
        with open(self.log_file_path, 'w', encoding='utf-8') as f:
            f.write(f"=== 测试执行日志 ===\n")
            f.write(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"="*50 + "\n\n")
        
        return self.log_file_path
    
    async def execute_task(self, task_id: int) -> Dict:
        """
        执行测试单
        
        Args:
            task_id: 测试单ID
        
        Returns:
            执行结果摘要
        """
        try:
            # 1. 查询测试单信息
            task = await TestUITask.get(id=task_id)
            
            # 2. 创建工作目录
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            work_dir = Path('test_executions') / f'task_{task_id}_{timestamp}'
            work_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"创建工作目录: {work_dir}")
            
            # 2.1 创建日志文件并保存路径
            log_file_path = self._create_log_file(work_dir)
            task.log_file_path = log_file_path
            await task.save(update_fields=['log_file_path'])
            
            self._add_log(f"开始执行测试单: task_id={task_id}")
            
            # 3. 获取用例列表
            case_ids = await self._expand_task_contents(task_id)
            
            self._add_log(f"测试单包含 {len(case_ids)} 个用例")
            logger.info(f"测试单包含 {len(case_ids)} 个用例")
            
            # 4. 生成配置文件
            config = await self.config_gen.generate_config(task, case_ids, work_dir)
            self._add_log("生成配置文件完成")
            
            # 5. 生成脚本文件
            scripts = []
            for idx, case_id in enumerate(case_ids, 1):
                script_info = await self.script_gen.generate_script(case_id, work_dir, idx)
                scripts.append(script_info)
            
            self._add_log(f"生成 {len(scripts)} 个脚本文件")
            logger.info(f"生成 {len(scripts)} 个脚本文件")
            
            # 6. 创建测试报告
            report = await TestUIReport.create(
                test_task_id=task_id,
                execution_time=datetime.now(),
                total_cases=len(case_ids),
                report_data={
                    'status': 'running',
                    'task_name': task.name,
                    'environment': task.environment,
                    'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            )
            
            # 7. 更新测试单状态
            task.status = TaskStatus.RUNNING
            task.start_time = datetime.now()
            task.total_cases = len(case_ids)
            await task.save()
            
            self._add_log(f"开始执行测试用例...")
            logger.info(f"开始执行测试单: task_id={task_id}, total_cases={len(case_ids)}")
            
            # 8. 执行测试用例
            results = await self._execute_cases(scripts, config, work_dir, task, report)
            
            # 9. 收集结果
            self._add_log("开始收集执行结果...")
            await self.result_collector.collect_results(work_dir, report.id)
            
            # 10. 更新测试单和报告
            await self._finalize_execution(task, report, results)
            
            self._add_log(f"测试单执行完成! 总数={len(results)}, 通过={task.passed_cases}, 失败={task.failed_cases}")
            logger.info(f"测试单执行完成: task_id={task_id}")
            
            return {
                'task_id': task_id,
                'status': task.status,
                'total_cases': len(case_ids),
                'passed_cases': task.passed_cases,
                'failed_cases': task.failed_cases,
                'work_dir': str(work_dir)
            }
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            error_msg = f"执行测试单失败: {type(e).__name__}: {str(e)}"
            self._add_log(error_msg, "ERROR")
            self._add_log(f"详细错误:\n{error_detail}", "ERROR")
            logger.error(f"执行测试单失败: task_id={task_id}, {type(e).__name__}: {e}")
            logger.error(f"堆栈信息:\n{error_detail}")
            # 更新任务状态为失败，并更新进度和报告
            try:
                task = await TestUITask.get(id=task_id)
                task.status = TaskStatus.FAILED
                task.end_time = datetime.now()
                
                # 更新执行统计（如果有的话）
                if hasattr(task, 'executed_cases') and task.executed_cases is not None:
                    # 已有执行进度，保留当前的统计
                    pass
                else:
                    # 未开始执行或初期失败，设置为0
                    task.executed_cases = 0
                    task.passed_cases = 0
                    task.failed_cases = 0
                    task.progress = Decimal('0.0')
                
                await task.save()
                
                # 尝试更新或创建报告
                error_report: Optional[TestUIReport] = None
                
                # 查找是否已创建报告
                try:
                    error_report = await TestUIReport.filter(test_task_id=task_id).order_by('-id').first()
                except:
                    pass
                
                duration = 0
                if task.start_time and task.end_time:
                    duration = int((task.end_time - task.start_time).total_seconds())
                
                if error_report:
                    # 更新现有报告
                    error_report.passed_cases = task.passed_cases or 0
                    error_report.failed_cases = task.failed_cases or 0
                    error_report.skipped_cases = (task.total_cases or 0) - (task.executed_cases or 0)
                    error_report.execution_duration = duration
                    error_report.pass_rate = Decimal('0.0')
                    error_report.report_data = {
                        'error': str(e),
                        'status': 'failed',
                        'message': '执行过程中出现异常'
                    }
                    await error_report.save()
                    logger.info(f"已更新失败报告: report_id={error_report.id}")
                else:
                    # 创建新报告
                    error_report = await TestUIReport.create(
                        test_task_id=task_id,
                        execution_time=datetime.now(),
                        total_cases=task.total_cases or 0,
                        passed_cases=task.passed_cases or 0,
                        failed_cases=task.failed_cases or 0,
                        skipped_cases=(task.total_cases or 0) - (task.executed_cases or 0),
                        execution_duration=duration,
                        pass_rate=Decimal('0.0'),
                        report_data={
                            'error': str(e),
                            'status': 'failed',
                            'message': '执行过程中出现异常'
                        }
                    )
                    logger.info(f"已创建失败报告: report_id={error_report.id}")
                    
            except Exception as inner_e:
                logger.error(f"更新失败状态时出错: {inner_e}")
            raise
    
    async def _expand_task_contents(self, task_id: int) -> List[int]:
        """展开测试单内容为用例ID列表"""
        contents = await TestUITaskContent.filter(
            test_task_id=task_id
        ).order_by('sort_order').all()
        
        case_ids = []
        seen = set()
        
        for content in contents:
            if content.item_type == TaskContentType.CASE:
                if content.item_id not in seen:
                    case_ids.append(content.item_id)
                    seen.add(content.item_id)
            
            elif content.item_type == TaskContentType.SUITE:
                # 查询套件包含的用例
                relations = await TestUICasesSuitesRelation.filter(
                    test_suite_id=content.item_id
                ).order_by('sort_order').all()
                
                for relation in relations:
                    # 获取用例 ID（Tortoise ORM 外键字段名 + _id）
                    case_id = getattr(relation, 'test_case_id', None)
                    if case_id and case_id not in seen:
                        case_ids.append(case_id)
                        seen.add(case_id)
        
        return case_ids
    
    async def _execute_cases(self, scripts: List[Dict], config: Dict, 
                            work_dir: Path, task: TestUITask, 
                            report: TestUIReport) -> List[Dict]:
        """执行所有用例脚本"""
        execute_config = config['execute_config']
        parallel_mode = execute_config.get('parallel_mode', 'process')
        
        if parallel_mode == 'serial':
            # 串行执行
            return await self._execute_serial(scripts, work_dir, task, report)
        else:
            # 并发执行
            return await self._execute_parallel(scripts, work_dir, task, report, execute_config)
    
    async def _execute_serial(self, scripts: List[Dict], work_dir: Path,
                             task: TestUITask, report: TestUIReport) -> List[Dict]:
        """串行执行用例脚本"""
        results = []
        
        for idx, script_info in enumerate(scripts, 1):
            case_name = script_info['case_name']
            self._add_log(f"正在执行用例 [{idx}/{len(scripts)}]: {case_name}")
            logger.info(f"执行用例 {idx}/{len(scripts)}: {case_name}")
            
            result = self.case_executor.execute_case_script(
                script_path=script_info['script_path'],
                work_dir=str(work_dir),
                timeout=300
            )
            
            status = result.get('status', 'unknown')
            if status == 'passed':
                self._add_log(f"✅ 用例 {case_name} 执行成功")
            else:
                error = result.get('error', '未知错误')
                self._add_log(f"❌ 用例 {case_name} 执行失败: {error}", "ERROR")
            
            results.append(result)
            
            # 更新进度
            await self._update_progress(task, idx, len(scripts))
        
        return results
    
    async def _execute_parallel(self, scripts: List[Dict], work_dir: Path,
                               task: TestUITask, report: TestUIReport,
                               execute_config: Dict) -> List[Dict]:
        """并发执行用例脚本"""
        max_workers = execute_config.get('max_workers', 4)
        if max_workers == 'auto':
            max_workers = multiprocessing.cpu_count()
        
        self._add_log(f"开始并发执行，并发数: {max_workers}")
        
        worker_timeout = execute_config.get('worker_timeout', 300)
        
        results = []
        
        # 使用进程池并发执行
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_script = {}
            for script_info in scripts:
                future = executor.submit(
                    self.case_executor.execute_case_script,
                    script_path=script_info['script_path'],
                    work_dir=str(work_dir),
                    timeout=worker_timeout
                )
                future_to_script[future] = script_info
            
            # 收集结果
            completed = 0
            for future in as_completed(future_to_script):
                script_info = future_to_script[future]
                case_name = script_info['case_name']
                try:
                    result = future.result(timeout=worker_timeout)
                    results.append(result)
                    completed += 1
                    
                    status = result.get('status', 'unknown')
                    if status == 'passed':
                        self._add_log(f"✅ 用例 {case_name} 执行成功 [{completed}/{len(scripts)}]")
                    else:
                        error = result.get('error', '未知错误')
                        self._add_log(f"❌ 用例 {case_name} 执行失败: {error} [{completed}/{len(scripts)}]", "ERROR")
                    
                    logger.info(f"用例执行完成 {completed}/{len(scripts)}: {case_name}")
                    
                    # 更新进度
                    await self._update_progress(task, completed, len(scripts))
                    
                except Exception as e:
                    self._add_log(f"❌ 用例 {case_name} 执行异常: {str(e)}", "ERROR")
                    logger.error(f"用例执行异常: {case_name}, {e}")
                    results.append({
                        'case_id': script_info['case_id'],
                        'status': 'failed',
                        'error': str(e)
                    })
        
        return results
    
    async def _update_progress(self, task: TestUITask, executed: int, total: int):
        """更新测试单执行进度"""
        try:
            task.executed_cases = executed
            task.progress = Decimal(str((executed / total * 100) if total > 0 else 0))
            await task.save()
        except Exception as e:
            logger.error(f"更新进度失败: {e}")
    
    async def _finalize_execution(self, task: TestUITask, report: TestUIReport, results: List[Dict]):
        """完成执行，更新最终状态"""
        try:
            # 统计结果
            passed_count = sum(1 for r in results if r.get('status') == 'passed')
            failed_count = sum(1 for r in results if r.get('status') == 'failed')
            
            # 更新测试单
            task.status = TaskStatus.COMPLETED
            task.end_time = datetime.now()
            task.passed_cases = passed_count
            task.failed_cases = failed_count
            task.progress = Decimal('100.0')
            await task.save()
            
            # 更新报告
            duration = 0
            if task.start_time and task.end_time:
                duration = int((task.end_time - task.start_time).total_seconds())
            
            report.passed_cases = passed_count
            report.failed_cases = failed_count
            report.skipped_cases = 0
            report.execution_duration = duration
            report.pass_rate = Decimal(str((passed_count / len(results) * 100) if len(results) > 0 else 0))
            await report.save()
            
            logger.info(f"测试执行完成: 总数={len(results)}, 通过={passed_count}, 失败={failed_count}")
            
        except Exception as e:
            logger.error(f"完成执行时出错: {e}")
