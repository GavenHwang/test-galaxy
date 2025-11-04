"""
UI自动化测试执行引擎
基于Playwright实现浏览器自动化
"""
from typing import Dict, Any, Optional
from datetime import datetime
from app.models.ui_test import (
    TestUITask,
    TestUICase,
    TestUIStep,
    TestUIElement,
    TestUIReport,
    TestUICaseExecutionRecord,
    TestUICaseStepExecutionRecord,
    TestUITaskContent,
    TaskStatus,
    ExecutionStatus
)

# Playwright导入（需要先安装: pip install playwright）
try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not installed. Execution engine disabled.")


class TestExecutionEngine:
    """测试执行引擎"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.current_task: Optional[TestUITask] = None
        self.current_report: Optional[TestUIReport] = None
    
    async def execute_task(self, task_id: int) -> Dict[str, Any]:
        """
        执行测试单
        
        Args:
            task_id: 测试单ID
            
        Returns:
            执行结果摘要
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise Exception("Playwright not installed")
        
        # 加载测试单
        task = await TestUITask.get_or_none(id=task_id)
        if not task:
            raise Exception(f"Test task {task_id} not found")
        
        self.current_task = task
        
        # 更新状态为执行中
        task.status = TaskStatus.RUNNING
        task.start_time = datetime.now()
        await task.save()
        
        # 创建测试报告
        report = await TestUIReport.create(
            test_task_id=task_id,
            start_time=datetime.now()
        )
        self.current_report = report
        
        try:
            # 初始化浏览器
            await self._init_browser(task.execute_config)
            
            # 执行测试内容
            total_cases = 0
            passed_cases = 0
            failed_cases = 0
            
            contents = await TestUITaskContent.filter(task_id=task_id).order_by('sort_order').all()
            
            for content in contents:
                if content.item_type == 'CASE':
                    # 执行单个用例
                    result = await self._execute_case(content.item_id, report.id)
                    total_cases += 1
                    if result['status'] == ExecutionStatus.PASSED:
                        passed_cases += 1
                    else:
                        failed_cases += 1
                
                elif content.item_type == 'SUITE':
                    # 执行套件（展开为用例）
                    from app.models.ui_test import TestUICasesSuitesRelation
                    relations = await TestUICasesSuitesRelation.filter(
                        suite_id=content.item_id
                    ).order_by('sort_order').all()
                    
                    for relation in relations:
                        result = await self._execute_case(relation.test_case_id, report.id)
                        total_cases += 1
                        if result['status'] == ExecutionStatus.PASSED:
                            passed_cases += 1
                        else:
                            failed_cases += 1
            
            # 更新报告
            report.total_cases = total_cases
            report.passed_cases = passed_cases
            report.failed_cases = failed_cases
            report.skipped_cases = 0
            report.pass_rate = (passed_cases / total_cases * 100) if total_cases > 0 else 0
            report.end_time = datetime.now()
            report.duration = int((report.end_time - report.start_time).total_seconds())
            await report.save()
            
            # 更新任务状态
            task.status = TaskStatus.COMPLETED
            task.end_time = datetime.now()
            task.total_cases = total_cases
            task.executed_cases = total_cases
            task.passed_cases = passed_cases
            task.failed_cases = failed_cases
            task.progress = 100.0
            await task.save()
            
            return {
                "status": "success",
                "total_cases": total_cases,
                "passed_cases": passed_cases,
                "failed_cases": failed_cases,
                "pass_rate": report.pass_rate,
                "duration": report.duration
            }
            
        except Exception as e:
            # 执行失败
            task.status = TaskStatus.FAILED
            await task.save()
            raise e
            
        finally:
            # 关闭浏览器
            await self._close_browser()
    
    async def _init_browser(self, config: Dict[str, Any]):
        """初始化浏览器"""
        browser_type = config.get('browser', 'chromium')
        headless = config.get('headless', True)
        
        async with async_playwright() as p:
            if browser_type == 'chromium':
                self.browser = await p.chromium.launch(headless=headless)
            elif browser_type == 'firefox':
                self.browser = await p.firefox.launch(headless=headless)
            elif browser_type == 'webkit':
                self.browser = await p.webkit.launch(headless=headless)
            else:
                self.browser = await p.chromium.launch(headless=headless)
            
            self.page = await self.browser.new_page()
    
    async def _close_browser(self):
        """关闭浏览器"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
    
    async def _execute_case(self, case_id: int, report_id: int) -> Dict[str, Any]:
        """
        执行单个测试用例
        
        Args:
            case_id: 用例ID
            report_id: 报告ID
            
        Returns:
            执行结果
        """
        case = await TestUICase.get_or_none(id=case_id)
        if not case:
            return {"status": ExecutionStatus.FAILED, "error": "Case not found"}
        
        # 创建用例执行记录
        case_record = await TestUICaseExecutionRecord.create(
            test_case_id=case_id,
            test_report_id=report_id,
            status=ExecutionStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            # 获取测试步骤
            steps = await TestUIStep.filter(test_case_id=case_id).order_by('sort_order').all()
            
            # 执行每个步骤
            for step in steps:
                step_result = await self._execute_step(step, case_record.id)
                
                if step_result['status'] == ExecutionStatus.FAILED:
                    # 步骤失败
                    case_record.status = ExecutionStatus.FAILED
                    case_record.error_message = step_result.get('error', 'Step failed')
                    case_record.end_time = datetime.now()
                    case_record.duration = int((case_record.end_time - case_record.start_time).total_seconds())
                    await case_record.save()
                    
                    return {"status": ExecutionStatus.FAILED, "error": step_result.get('error')}
            
            # 所有步骤通过
            case_record.status = ExecutionStatus.PASSED
            case_record.end_time = datetime.now()
            case_record.duration = int((case_record.end_time - case_record.start_time).total_seconds())
            await case_record.save()
            
            return {"status": ExecutionStatus.PASSED}
            
        except Exception as e:
            case_record.status = ExecutionStatus.FAILED
            case_record.error_message = str(e)
            case_record.end_time = datetime.now()
            case_record.duration = int((case_record.end_time - case_record.start_time).total_seconds())
            await case_record.save()
            
            return {"status": ExecutionStatus.FAILED, "error": str(e)}
    
    async def _execute_step(self, step: TestUIStep, case_execution_id: int) -> Dict[str, Any]:
        """
        执行单个测试步骤
        
        Args:
            step: 步骤对象
            case_execution_id: 用例执行记录ID
            
        Returns:
            执行结果
        """
        # 创建步骤执行记录
        step_record = await TestUICaseStepExecutionRecord.create(
            case_execution_id=case_execution_id,
            step_number=step.step_number,
            action=step.action,
            status=ExecutionStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            # 获取定位器
            selector = None
            if step.element_id:
                element = await TestUIElement.get_or_none(id=step.element_id)
                if element:
                    selector = self._build_selector(element.selector_type, element.selector_value)
            
            # 执行操作
            await self._perform_action(
                action=step.action,
                selector=selector,
                input_data=step.input_data,
                wait_time=step.wait_time
            )
            
            # 步骤成功
            step_record.status = ExecutionStatus.PASSED
            step_record.end_time = datetime.now()
            step_record.duration = int((step_record.end_time - step_record.start_time).total_seconds())
            await step_record.save()
            
            return {"status": ExecutionStatus.PASSED}
            
        except Exception as e:
            step_record.status = ExecutionStatus.FAILED
            step_record.error_message = str(e)
            step_record.end_time = datetime.now()
            step_record.duration = int((step_record.end_time - step_record.start_time).total_seconds())
            await step_record.save()
            
            return {"status": ExecutionStatus.FAILED, "error": str(e)}
    
    def _build_selector(self, selector_type: str, selector_value: str) -> str:
        """构建Playwright选择器"""
        if selector_type == 'ID':
            return f'#{selector_value}'
        elif selector_type == 'CSS':
            return selector_value
        elif selector_type == 'XPATH':
            return f'xpath={selector_value}'
        elif selector_type == 'TEXT':
            return f'text={selector_value}'
        elif selector_type == 'TEST_ID':
            return f'[data-testid="{selector_value}"]'
        else:
            return selector_value
    
    async def _perform_action(self, action: str, selector: Optional[str], input_data: Optional[str], wait_time: int):
        """执行具体操作"""
        if not self.page:
            raise Exception("Browser page not initialized")
        
        # 等待
        if wait_time and wait_time > 0:
            await self.page.wait_for_timeout(wait_time)
        
        # 执行操作
        if action == 'navigate':
            await self.page.goto(input_data)
        
        elif action == 'click':
            await self.page.click(selector)
        
        elif action == 'type':
            await self.page.fill(selector, input_data)
        
        elif action == 'select':
            await self.page.select_option(selector, input_data)
        
        elif action == 'wait':
            await self.page.wait_for_timeout(int(input_data) if input_data else 1000)
        
        elif action == 'wait_for_element':
            await self.page.wait_for_selector(selector)
        
        elif action == 'assert_text':
            text = await self.page.text_content(selector)
            assert text == input_data, f"Expected '{input_data}', got '{text}'"
        
        elif action == 'assert_exists':
            is_visible = await self.page.is_visible(selector)
            assert is_visible, f"Element '{selector}' not visible"
        
        elif action == 'screenshot':
            await self.page.screenshot(path=f'screenshot_{datetime.now().timestamp()}.png')
        
        elif action == 'hover':
            await self.page.hover(selector)
        
        elif action == 'clear':
            await self.page.fill(selector, '')
        
        elif action == 'execute_script':
            await self.page.evaluate(input_data)
        
        else:
            raise Exception(f"Unknown action: {action}")


# 全局执行引擎实例
execution_engine = TestExecutionEngine()
