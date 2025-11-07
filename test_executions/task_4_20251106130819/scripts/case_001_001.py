"""
测试用例自动生成脚本
用例ID: 1
用例名称: 用户登录功能测试
优先级: CasePriority.HIGH
模块: 用户管理
生成时间: 2025-11-06 13:08:19

执行方式：
    python case_001_001.py
    
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
LOG_PATH = WORK_DIR / "logs" / "case_001_001.json"
SCREENSHOT_DIR = WORK_DIR / "screenshots"

# 用例信息
CASE_ID = 1
CASE_NAME = "用户登录功能测试"
CASE_PRIORITY = "CasePriority.HIGH"
CASE_MODULE = "用户管理"

# 环境变量配置
DEBUG = os.getenv('DEBUG', '0') == '1'
HEADLESS = os.getenv('HEADLESS', '1') == '1'
SLOW_MO = int(os.getenv('SLOW_MO', '0'))

# ==================== 日志记录 ====================

class ExecutionLogger:
    """执行日志记录器"""
    
    def __init__(self, log_path):
        self.log_path = log_path
        self.log_data = {
            "case_info": {
                "case_id": CASE_ID,
                "case_name": CASE_NAME,
                "priority": CASE_PRIORITY,
                "module": CASE_MODULE
            },
            "execution_info": {
                "start_time": None,
                "end_time": None,
                "duration": 0,
                "status": "执行中",
                "error_message": None
            },
            "steps": [],
            "retry_count": 0,
            "screenshots": []
        }
    
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
    
    def log_step(self, step_number, action, description, status, duration, error_message=None, screenshot_path=None):
        """记录步骤执行"""
        step_log = {
            "step_number": step_number,
            "action": action,
            "description": description,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "duration": duration,
            "status": status,
            "error_message": error_message,
            "screenshot_path": screenshot_path
        }
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
        print(f"加载配置文件失败: {e}")
        sys.exit(1)

# ==================== 截图工具 ====================

async def take_screenshot(page, step_number):
    """截取屏幕截图"""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"case_{CASE_ID:03d}_step_{step_number:03d}_{timestamp}.png"
    screenshot_path = SCREENSHOT_DIR / filename
    await page.screenshot(path=str(screenshot_path))
    return str(screenshot_path.relative_to(WORK_DIR))

# ==================== 主测试函数 ====================

async def test_case_1():
    """用例主函数"""
    logger = ExecutionLogger(LOG_PATH)
    logger.start_execution()
    
    config = load_config()
    execute_config = config['execute_config']
    
    # 获取测试用户（如果配置了权限）
    # 使用环境变量中的默认用户
test_user = {
    'username': config['environment_variables'].get('admin_username'),
    'password': config['environment_variables'].get('admin_password')
}
    
    try:
        async with async_playwright() as p:
            # 启动浏览器
            browser_type = execute_config.get('browser', 'chromium')
            browser_args = {
                'headless': HEADLESS if not DEBUG else False,
                'slow_mo': SLOW_MO
            }
            
            if browser_type == 'chromium':
                browser = await p.chromium.launch(**browser_args)
            elif browser_type == 'firefox':
                browser = await p.firefox.launch(**browser_args)
            elif browser_type == 'webkit':
                browser = await p.webkit.launch(**browser_args)
            else:
                browser = await p.chromium.launch(**browser_args)
            
            # 创建页面
            viewport = execute_config.get('viewport', {'width': 1920, 'height': 1080})
            page = await browser.new_page(viewport=viewport)
            
            # 设置默认超时
            default_timeout = execute_config.get('timeout', 30000)
            page.set_default_timeout(default_timeout)
            
            try:
                # 步骤 1: 导航到登录页
step_start = datetime.now()
try:
    await page.wait_for_timeout(2000)
    await page.goto("https://itos2.sugon.com/sso/login")
    step_duration = int((datetime.now() - step_start).total_seconds() * 1000)
    logger.log_step(1, "navigate", "导航到登录页", "通过", step_duration)
    if DEBUG:
        print(f"  ✓ 步骤 1: 导航到登录页")
except Exception as e:
    step_duration = int((datetime.now() - step_start).total_seconds() * 1000)
    screenshot_path = None
    if execute_config.get('auto_screenshot', True):
        screenshot_path = await take_screenshot(page, 1)
    logger.log_step(1, "navigate", "导航到登录页", "失败", step_duration, str(e), screenshot_path)
    raise

# 步骤 2: 输入用户名
step_start = datetime.now()
try:
    await page.fill("#username", "api_common_01")
    step_duration = int((datetime.now() - step_start).total_seconds() * 1000)
    logger.log_step(2, "type", "输入用户名", "通过", step_duration)
    if DEBUG:
        print(f"  ✓ 步骤 2: 输入用户名")
except Exception as e:
    step_duration = int((datetime.now() - step_start).total_seconds() * 1000)
    screenshot_path = None
    if execute_config.get('auto_screenshot', True):
        screenshot_path = await take_screenshot(page, 2)
    logger.log_step(2, "type", "输入用户名", "失败", step_duration, str(e), screenshot_path)
    raise

# 步骤 3: 输入密码
step_start = datetime.now()
try:
    await page.fill("#password", "111111aA")
    step_duration = int((datetime.now() - step_start).total_seconds() * 1000)
    logger.log_step(3, "type", "输入密码", "通过", step_duration)
    if DEBUG:
        print(f"  ✓ 步骤 3: 输入密码")
except Exception as e:
    step_duration = int((datetime.now() - step_start).total_seconds() * 1000)
    screenshot_path = None
    if execute_config.get('auto_screenshot', True):
        screenshot_path = await take_screenshot(page, 3)
    logger.log_step(3, "type", "输入密码", "失败", step_duration, str(e), screenshot_path)
    raise

# 步骤 4: 点击登录
step_start = datetime.now()
try:
    await page.wait_for_timeout(2000)
    await page.click("#submitBtn")
    step_duration = int((datetime.now() - step_start).total_seconds() * 1000)
    logger.log_step(4, "click", "点击登录", "通过", step_duration)
    if DEBUG:
        print(f"  ✓ 步骤 4: 点击登录")
except Exception as e:
    step_duration = int((datetime.now() - step_start).total_seconds() * 1000)
    screenshot_path = None
    if execute_config.get('auto_screenshot', True):
        screenshot_path = await take_screenshot(page, 4)
    logger.log_step(4, "click", "点击登录", "失败", step_duration, str(e), screenshot_path)
    raise
                
                # 所有步骤通过
                logger.end_execution("通过")
                print(f"✓ 用例执行成功: {CASE_NAME}")
                sys.exit(0)
                
            except Exception as step_error:
                # 步骤执行失败
                error_msg = f"{type(step_error).__name__}: {str(step_error)}"
                logger.end_execution("失败", error_msg)
                
                # 失败截图
                if execute_config.get('auto_screenshot', True):
                    try:
                        screenshot_path = await take_screenshot(page, 999)
                        logger.log_data["screenshots"].append(screenshot_path)
                        logger._write_log()
                    except:
                        pass
                
                print(f"✗ 用例执行失败: {CASE_NAME}")
                print(f"  错误信息: {error_msg}")
                if DEBUG:
                    traceback.print_exc()
                sys.exit(1)
            
            finally:
                await browser.close()
    
    except Exception as e:
        # 浏览器启动失败
        error_msg = f"浏览器初始化失败: {str(e)}"
        logger.end_execution("失败", error_msg)
        print(f"✗ {error_msg}")
        if DEBUG:
            traceback.print_exc()
        sys.exit(1)

# ==================== 脚本入口 ====================

if __name__ == "__main__":
    print(f"开始执行用例: {CASE_NAME} (ID: {CASE_ID})")
    asyncio.run(test_case_1())
