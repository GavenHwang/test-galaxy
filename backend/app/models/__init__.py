"""
ORM数据库映射
"""
# 新增model需要在这里导入
from .user import User, Role, Menu
from .env import Env, Component, ComponentVersion, Project
from .ui_test import (
    SelectorType, ActionType, CasePriority, CaseStatus,
    TaskStatus, TaskContentType, ExecutionStatus,
    TestCommonUser, TestUIElement, TestUIElementPermission,
    TestUICase, TestUICasePermission, TestUIStep, TestUICaseSuite,
    TestUICasesSuitesRelation, TestUITask, TestUITaskContent,
    TestUIReport, TestUICaseExecutionRecord, TestUICaseStepExecutionRecord,
    TestProductRole  # 新增产品角色模型
)

__all__ = [
    # user models
    'User', 'Role', 'Menu',
    # env models
    'Env', 'Component', 'ComponentVersion', 'Project',
    # ui_test enums
    'SelectorType', 'ActionType', 'CasePriority', 'CaseStatus',
    'TaskStatus', 'TaskContentType', 'ExecutionStatus',
    # ui_test models
    'TestCommonUser', 'TestUIElement', 'TestUIElementPermission',
    'TestUICase', 'TestUICasePermission', 'TestUIStep', 'TestUICaseSuite',
    'TestUICasesSuitesRelation', 'TestUITask', 'TestUITaskContent',
    'TestUIReport', 'TestUICaseExecutionRecord', 'TestUICaseStepExecutionRecord',
    'TestProductRole'  # 新增产品角色模型
]