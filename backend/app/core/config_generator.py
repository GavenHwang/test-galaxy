"""
配置生成器
负责生成测试执行所需的配置文件
"""
import json
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

from app.models.ui_test import (
    TestUITask,
    TestCommonUser,
    TestUICasePermission
)
from app.log import logger


class ConfigGenerator:
    """
    配置生成器
    负责生成测试执行所需的配置文件
    """
    
    async def generate_config(self, task: TestUITask, case_ids: List[int], work_dir: Path) -> Dict:
        """
        生成配置文件
        
        Args:
            task: 测试单对象
            case_ids: 用例ID列表
            work_dir: 工作目录
        
        Returns:
            配置数据字典
        """
        try:
            # 1. 收集所有涉及的权限角色
            role_names = await self._collect_role_names(case_ids)
            
            # 2. 为每个角色查找测试用户
            test_users = await self._load_test_users(role_names, task.environment)
            
            # 3. 构建配置数据
            config = {
                'task_info': {
                    'task_id': task.id,
                    'task_name': task.name,
                    'environment': task.environment,
                    'created_by': task.created_by,
                    'created_time': task.created_time.strftime('%Y-%m-%d %H:%M:%S')
                },
                'execute_config': task.execute_config or {},
                'test_users': test_users,
                'environment_variables': self._get_environment_variables(task.environment)
            }
            
            # 确保 execute_config 包含必要的默认值
            if 'browser' not in config['execute_config']:
                config['execute_config']['browser'] = 'chromium'
            if 'headless' not in config['execute_config']:
                config['execute_config']['headless'] = True
            if 'timeout' not in config['execute_config']:
                config['execute_config']['timeout'] = 30000  # 默认 30 秒
            else:
                # 将用户设置的超时时间（秒）转换为毫秒
                timeout_value = config['execute_config']['timeout']
                if isinstance(timeout_value, (int, float)) and timeout_value < 1000:
                    # 如果值小于 1000，认为是秒，需要转换为毫秒
                    config['execute_config']['timeout'] = int(timeout_value * 1000)
            if 'continue_on_failure' not in config['execute_config']:
                config['execute_config']['continue_on_failure'] = True
            if 'retry_count' not in config['execute_config']:
                config['execute_config']['retry_count'] = 2
            if 'auto_screenshot' not in config['execute_config']:
                config['execute_config']['auto_screenshot'] = True
            if 'viewport' not in config['execute_config']:
                config['execute_config']['viewport'] = {'width': 1920, 'height': 1080}
            
            # 4. 写入配置文件
            config_path = work_dir / 'config.json'
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"配置文件生成成功: {config_path}")
            return config
            
        except Exception as e:
            logger.error(f"生成配置文件失败: {e}")
            raise
    
    async def _collect_role_names(self, case_ids: List[int]) -> Set[str]:
        """收集所有用例的权限角色"""
        permissions = await TestUICasePermission.filter(
            test_case_id__in=case_ids
        ).all()
        return set(p.role_name for p in permissions)
    
    async def _load_test_users(self, role_names: Set[str], environment: str) -> Dict:
        """为每个角色加载测试用户"""
        test_users = {}
        for role_name in role_names:
            # 查找匹配角色的用户
            user = await TestCommonUser.filter(
                role_name=role_name
            ).first()
            
            if user:
                test_users[role_name] = {
                    'username': user.username,
                    'password': user.password
                }
            else:
                # 记录警告：找不到匹配用户
                logger.warn(f"找不到角色 '{role_name}' 的测试用户")
        
        return test_users
    
    def _get_environment_variables(self, environment: str) -> Dict:
        """获取环境变量配置"""
        # 这里可以从数据库或配置文件读取环境相关变量
        # 示例：根据环境名称返回不同的配置
        env_map = {
            '测试环境': {
                'host': 'http://localhost:5173',
                'api_host': 'http://localhost:9998'
            },
            '生产环境': {
                'host': 'http://www.example.com',
                'api_host': 'http://api.example.com'
            }
        }
        
        return env_map.get(environment, {
            'host': 'http://localhost:5173',
            'api_host': 'http://localhost:9998',
            'admin_username': 'admin',
            'admin_password': '111111aA'
        })
