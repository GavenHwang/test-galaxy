"""
脚本生成器
负责为每个测试用例生成独立的 Playwright Python 脚本
"""
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

from app.models.ui_test import (
    TestUICase,
    TestUIStep,
    TestUIElement,
    TestUICasePermission
)
from app.core.selector_builder import SelectorBuilder
from app.log import logger


class ScriptGenerator:
    """
    脚本生成器
    为每个测试用例生成独立的 Python 脚本文件
    """
    
    def __init__(self):
        self.selector_builder = SelectorBuilder()
    
    async def generate_script(self, case_id: int, work_dir: Path, sequence: int) -> Dict:
        """
        生成用例脚本
        
        Args:
            case_id: 用例ID
            work_dir: 工作目录
            sequence: 脚本序号
        
        Returns:
            脚本信息字典
        """
        try:
            # 1. 查询用例基本信息
            case = await TestUICase.get(id=case_id)
            
            # 2. 查询用例步骤及关联元素
            steps = await TestUIStep.filter(test_case_id=case_id).order_by('sort_order').all()
            
            # 3. 查询用例权限角色
            permissions = await TestUICasePermission.filter(test_case_id=case_id).all()
            role_names = [p.role_name for p in permissions]
            
            # 4. 生成用户加载代码
            user_loading_code = self._generate_user_loading_code(role_names)
            
            # 5. 生成步骤执行代码
            steps_code = await self._generate_steps_code(steps)
            
            # 6. 使用模板生成完整脚本
            script_content = self._render_template(
                case_id=case_id,
                case_name=case.name,
                priority=case.priority,
                module=case.module or '',
                sequence=sequence,
                user_loading_code=user_loading_code,
                steps_execution_code=steps_code
            )
            
            # 7. 写入脚本文件
            script_path = work_dir / 'scripts' / f'case_{case_id:03d}_{sequence:03d}.py'
            script_path.parent.mkdir(parents=True, exist_ok=True)
            script_path.write_text(script_content, encoding='utf-8')
            
            logger.info(f"脚本文件生成成功: {script_path}")
            
            return {
                'case_id': case_id,
                'case_name': case.name,
                'script_path': str(script_path),
                'sequence': sequence
            }
            
        except Exception as e:
            logger.error(f"生成脚本失败 (case_id={case_id}): {e}")
            raise
    
    def _generate_user_loading_code(self, role_names: List[str]) -> str:
        """生成用户加载代码"""
        if not role_names:
            # 无权限配置，使用默认用户
            return """    # 使用环境变量中的默认用户
    test_user = {
        'username': config['environment_variables'].get('admin_username'),
        'password': config['environment_variables'].get('admin_password')
    }"""
        else:
            # 有权限配置，使用指定角色的用户
            role_name = role_names[0]  # 使用第一个角色
            return f"""    # 从配置中获取指定角色的测试用户
    role_name = "{role_name}"
    if role_name in config['test_users']:
        test_user = config['test_users'][role_name]
    else:
        # 回退到默认用户
        test_user = {{
            'username': config['environment_variables'].get('admin_username'),
            'password': config['environment_variables'].get('admin_password')
        }}"""
    
    async def _generate_steps_code(self, steps: List[TestUIStep]) -> str:
        """生成步骤执行代码"""
        steps_code_list = []
        
        for idx, step in enumerate(steps, 1):
            step_code = await self._generate_single_step_code(step, idx)
            steps_code_list.append(step_code)
        
        return '\n\n'.join(steps_code_list)
    
    async def _generate_single_step_code(self, step: TestUIStep, step_number: int) -> str:
        """生成单个步骤的代码"""
        # 获取元素选择器
        selector = ""
        if step.element_id:
            element = await TestUIElement.get_or_none(id=step.element_id)
            if element:
                selector = self.selector_builder.build_selector(
                    element.selector_type,
                    element.selector_value
                )
        
        # 处理输入数据（替换配置变量）
        input_data = self._process_input_data(step.input_data)
        
        # 生成步骤代码
        action_code = self._generate_action_code(
            action=step.action,
            selector=selector,
            input_data=input_data,
            wait_time=step.wait_time
        )
        
        # 组装完整的步骤代码（包含异常处理和日志记录）
        step_template = f"""                # 步骤 {step_number}: {step.description}
                step_start = datetime.now()
                try:
                    {action_code}
                    step_duration = int((datetime.now() - step_start).total_seconds() * 1000)
                    logger.log_step({step_number}, "{step.action}", "{step.description}", "通过", step_duration, step_start_time=step_start)
                    if DEBUG:
                        print(f"  ✓ 步骤 {step_number}: {step.description}")
                except Exception as e:
                    step_duration = int((datetime.now() - step_start).total_seconds() * 1000)
                    screenshot_path = None
                    if execute_config.get('auto_screenshot', True):
                        screenshot_path = await take_screenshot(page, {step_number})
                    logger.log_step({step_number}, "{step.action}", "{step.description}", "失败", step_duration, str(e), screenshot_path, step_start)
                    raise"""
        
        return step_template
    
    def _process_input_data(self, input_data: str) -> str:
        """处理输入数据，替换配置变量"""
        if not input_data:
            return "None"
        
        # 检查是否包含变量占位符
        if '{{' in input_data and '}}' in input_data:
            # 提取变量名
            import re
            variables = re.findall(r'\{\{(\w+)\}\}', input_data)
            
            for var in variables:
                if var in ['username', 'password']:
                    # 替换为 test_user 变量
                    input_data = input_data.replace(f'{{{{{var}}}}}', f"{{test_user['{var}']}}")
                else:
                    # 替换为环境变量
                    input_data = input_data.replace(f'{{{{{var}}}}}', f"{{config['environment_variables'].get('{var}')}}")
            
            # 返回 f-string 格式
            return f'f"{input_data}"'
        else:
            # 转义引号
            input_data = input_data.replace('"', '\\"')
            return f'"{input_data}"'
    
    def _generate_action_code(self, action: str, selector: str, input_data: str, wait_time: int) -> str:
        """根据操作类型生成对应的 Playwright 代码"""
        # 处理等待时间
        wait_code = ""
        if wait_time and wait_time > 0:
            wait_code = f"await page.wait_for_timeout({wait_time})\n                    "
        
        # 根据操作类型生成代码
        action_map = {
            'navigate': f'{wait_code}await page.goto({input_data})',
            'click': f'{wait_code}await page.click("{selector}")',
            'type': f'{wait_code}await page.fill("{selector}", {input_data})',
            'select': f'{wait_code}await page.select_option("{selector}", {input_data})',
            'wait': f'await page.wait_for_timeout({input_data if input_data != "None" else 1000})',
            'wait_for_element': f'{wait_code}await page.wait_for_selector("{selector}")',
            'assert_text': f'{wait_code}actual_text = await page.text_content("{selector}")\n                    expected_text = {input_data}\n                    assert actual_text == expected_text, f"期望文本 \'{{expected_text}}\', 实际文本 \'{{actual_text}}\'"',
            'assert_exists': f'{wait_code}is_visible = await page.is_visible("{selector}")\n                    assert is_visible, f"元素 \'{selector}\' 不可见"',
            'screenshot': f'{wait_code}await take_screenshot(page, 0)',
            'hover': f'{wait_code}await page.hover("{selector}")',
            'clear': f'{wait_code}await page.fill("{selector}", "")',
            'execute_script': f'{wait_code}await page.evaluate({input_data})',
            'go_back': f'{wait_code}await page.go_back()',
            'refresh': f'{wait_code}await page.reload()'
        }
        
        return action_map.get(action, f'# Unknown action: {action}')
    
    def _render_template(self, **kwargs) -> str:
        """渲染脚本模板"""
        template = '''"""
测试用例自动生成脚本
用例ID: {case_id}
用例名称: {case_name}
优先级: {priority}
模块: {module}
生成时间: {generated_time}

执行方式：
    python {script_filename}
    
环境变量：
    DEBUG=1 启用详细日志
    HEADLESS=0 使用有头模式
    SLOW_MO=500 减慢操作速度
"""

import asyncio
import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# ==================== 全局配置 ====================

SCRIPT_DIR = Path(__file__).parent
WORK_DIR = SCRIPT_DIR.parent
CONFIG_PATH = WORK_DIR / "config.json"
LOG_PATH = WORK_DIR / "logs" / "case_{case_id:03d}_{sequence:03d}.json"
SCREENSHOT_DIR = WORK_DIR / "screenshots"

# 用例信息
CASE_ID = {case_id}
CASE_NAME = "{case_name}"
CASE_PRIORITY = "{priority}"
CASE_MODULE = "{module}"

# 环境变量配置
DEBUG = os.getenv('DEBUG', '0') == '1'
HEADLESS = os.getenv('HEADLESS', '1') == '1'
SLOW_MO = int(os.getenv('SLOW_MO', '0'))

# ==================== 日志记录 ====================

class ExecutionLogger:
    """执行日志记录器"""
    
    def __init__(self, log_path):
        self.log_path = log_path
        self.log_data = {{
            "case_info": {{
                "case_id": CASE_ID,
                "case_name": CASE_NAME,
                "priority": CASE_PRIORITY,
                "module": CASE_MODULE
            }},
            "execution_info": {{
                "start_time": None,
                "end_time": None,
                "duration": 0,
                "status": "执行中",
                "error_message": None
            }},
            "steps": [],
            "retry_count": 0,
            "screenshots": []
        }}
    
    def start_execution(self):
        """记录执行开始"""
        self.log_data["execution_info"]["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._write_log()
    
    def end_execution(self, status, error_message=None):
        """记录执行结束"""
        end_time = datetime.now()
        start_time = datetime.strptime(
            self.log_data["execution_info"]["start_time"],
            "%Y-%m-%d %H:%M:%S"
        )
        duration = int((end_time - start_time).total_seconds())
        
        self.log_data["execution_info"]["end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
        self.log_data["execution_info"]["duration"] = duration
        self.log_data["execution_info"]["status"] = status
        self.log_data["execution_info"]["error_message"] = error_message
        self._write_log()
    
    def log_step(self, step_number, action, description, status, duration, error_message=None, screenshot_path=None, step_start_time=None):
        """记录步骤执行"""
        # 计算结束时间
        end_time = datetime.now()
        if step_start_time:
            start_time = step_start_time
        else:
            # 如果没有传入开始时间，通过 duration 回推
            from datetime import timedelta
            start_time = end_time - timedelta(milliseconds=duration)
        
        step_log = {{
            "step_number": step_number,
            "action": action,
            "description": description,
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration": duration,
            "status": status,
            "error_message": error_message,
            "screenshot_path": screenshot_path
        }}
        self.log_data["steps"].append(step_log)
        
        if screenshot_path:
            self.log_data["screenshots"].append(screenshot_path)
        
        self._write_log()
    
    def increment_retry(self):
        """增加重试计数"""
        self.log_data["retry_count"] += 1
        self._write_log()
    
    def _write_log(self):
        """写入日志文件"""
        os.makedirs(self.log_path.parent, exist_ok=True)
        with open(self.log_path, 'w', encoding='utf-8') as f:
            json.dump(self.log_data, f, ensure_ascii=False, indent=2)

# ==================== 配置加载 ====================

def load_config():
    """加载配置文件"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载配置文件失败: {{e}}")
        sys.exit(1)

# ==================== 截图工具 ====================

async def take_screenshot(page, step_number):
    """截取屏幕截图"""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"case_{{{{CASE_ID:03d}}}}_step_{{{{step_number:03d}}}}_{{{{timestamp}}}}.png"
    screenshot_path = SCREENSHOT_DIR / filename
    # 截图时设置较长的超时时间，避免因字体加载等原因导致超时
    await page.screenshot(path=str(screenshot_path), timeout=10000)
    return str(screenshot_path.relative_to(WORK_DIR))

# ==================== 主测试函数 ====================

async def test_case_{case_id}():
    """用例主函数"""
    logger = ExecutionLogger(LOG_PATH)
    logger.start_execution()
    
    config = load_config()
    execute_config = config['execute_config']
    
    # 获取测试用户（如果配置了权限）
    {user_loading_code}
    
    try:
        async with async_playwright() as p:
            # 启动浏览器
            browser_type = execute_config.get('browser', 'chromium')
            browser_args = {{
                'headless': HEADLESS if not DEBUG else False,
                'slow_mo': SLOW_MO
            }}
            
            if browser_type == 'chromium':
                browser = await p.chromium.launch(**browser_args)
            elif browser_type == 'firefox':
                browser = await p.firefox.launch(**browser_args)
            elif browser_type == 'webkit':
                browser = await p.webkit.launch(**browser_args)
            else:
                browser = await p.chromium.launch(**browser_args)
            
            # 创建页面
            viewport = execute_config.get('viewport', {{'width': 1920, 'height': 1080}})
            page = await browser.new_page(viewport=viewport)
            
            # 设置默认超时
            default_timeout = execute_config.get('timeout', 30000)
            page.set_default_timeout(default_timeout)
            
            try:
                {steps_execution_code}
                
                # 所有步骤通过
                logger.end_execution("通过")
                print(f"✓ 用例执行成功: {{CASE_NAME}}")
                sys.exit(0)
                
            except Exception as step_error:
                # 步骤执行失败
                error_msg = f"{{type(step_error).__name__}}: {{str(step_error)}}"
                logger.end_execution("失败", error_msg)
                
                # 失败截图
                if execute_config.get('auto_screenshot', True):
                    try:
                        screenshot_path = await take_screenshot(page, 999)
                        logger.log_data["screenshots"].append(screenshot_path)
                        logger._write_log()
                    except:
                        pass
                
                print(f"✗ 用例执行失败: {{CASE_NAME}}")
                print(f"  错误信息: {{error_msg}}")
                if DEBUG:
                    traceback.print_exc()
                sys.exit(1)
            
            finally:
                await browser.close()
    
    except Exception as e:
        # 浏览器启动失败
        error_msg = f"浏览器初始化失败: {{{{str(e)}}}}"
        logger.end_execution("失败", error_msg)
        print(f"✗ {{{{error_msg}}}}")
        if DEBUG:
            traceback.print_exc()
        sys.exit(1)

# ==================== 脚本入口 ====================

if __name__ == "__main__":
    print(f"开始执行用例: {{CASE_NAME}} (ID: {{CASE_ID}})")
    asyncio.run(test_case_{case_id}())
'''
        
        # 填充模板变量
        kwargs['generated_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        kwargs['script_filename'] = f"case_{kwargs['case_id']:03d}_{kwargs['sequence']:03d}.py"
        
        return template.format(**kwargs)
