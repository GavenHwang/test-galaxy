"""
用例执行器
负责执行单个用例脚本
"""
import subprocess
import sys
from pathlib import Path
from typing import Dict

from app.log import logger


class CaseExecutor:
    """
    用例执行器
    使用 subprocess 执行独立脚本文件
    """
    
    def execute_case_script(self, script_path: str, work_dir: str, timeout: int = 300) -> Dict:
        """
        执行单个用例脚本（在独立进程中运行）
        
        Args:
            script_path: 脚本文件路径
            work_dir: 工作目录
            timeout: 超时时间（秒）
        
        Returns:
            执行结果字典
        """
        try:
            logger.info(f"开始执行脚本: {script_path}")
            
            # 执行脚本（script_path 是绝对路径，不需要设置 cwd）
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待执行完成
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                exit_code = process.returncode
                
                # 解析结果
                if exit_code == 0:
                    logger.info(f"脚本执行成功: {script_path}")
                    return {'status': 'passed', 'exit_code': exit_code, 'stdout': stdout}
                else:
                    # 收集错误信息：优先使用 stderr，如果为空则使用 stdout 的最后几行
                    error_msg = stderr.strip() if stderr.strip() else ''
                    if not error_msg and stdout.strip():
                        # 从 stdout 中提取错误信息（最后 10 行）
                        stdout_lines = stdout.strip().split('\n')
                        error_msg = '\n'.join(stdout_lines[-10:])
                    
                    if not error_msg:
                        error_msg = f'脚本执行失败，退出码: {exit_code}'
                    
                    logger.warn(f"脚本执行失败: {script_path}, exit_code={exit_code}")
                    logger.warn(f"错误信息:\n{error_msg}")
                    
                    return {
                        'status': 'failed',
                        'exit_code': exit_code,
                        'stdout': stdout,
                        'stderr': stderr,
                        'error': error_msg
                    }
            
            except subprocess.TimeoutExpired:
                process.kill()
                logger.error(f"脚本执行超时: {script_path}")
                return {'status': 'failed', 'error': '执行超时'}
        
        except Exception as e:
            logger.error(f"脚本执行异常: {script_path}, {e}")
            return {'status': 'failed', 'error': str(e)}
