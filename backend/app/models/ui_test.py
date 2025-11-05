"""
UI自动化测试平台 - ORM模型定义
"""
from enum import Enum

from tortoise import fields

from app.models.base import BaseModel, TimestampMixin

__all__ = [
    'SelectorType', 'ActionType', 'CasePriority', 'CaseStatus', 
    'TaskStatus', 'TaskContentType', 'ExecutionStatus',
    'TestCommonUser', 'TestUIElement', 'TestUIElementPermission',
    'TestUICase', 'TestUICasePermission', 'TestUIStep', 'TestUICaseSuite',
    'TestUICasesSuitesRelation', 'TestUITask', 'TestUITaskContent',
    'TestUIReport', 'TestUICaseExecutionRecord', 'TestUICaseStepExecutionRecord',
    'TestProductRole'  # 新增产品角色字典表
]


# ==================== 枚举定义 ====================

class SelectorType(str, Enum):
    """元素定位器类型"""
    ID = "ID"
    NAME = "NAME"
    CSS = "CSS"
    XPATH = "XPATH"
    CLASS_NAME = "CLASS_NAME"
    TAG_NAME = "TAG_NAME"
    LINK_TEXT = "LINK_TEXT"
    PARTIAL_LINK_TEXT = "PARTIAL_LINK_TEXT"
    TEST_ID = "TEST_ID"


class ActionType(str, Enum):
    """测试步骤操作类型"""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SELECT = "select"
    WAIT = "wait"
    WAIT_FOR_ELEMENT = "wait_for_element"
    ASSERT_TEXT = "assert_text"
    ASSERT_EXISTS = "assert_exists"
    SCREENSHOT = "screenshot"
    HOVER = "hover"
    CLEAR = "clear"
    EXECUTE_SCRIPT = "execute_script"
    SWITCH_FRAME = "switch_frame"
    GO_BACK = "go_back"
    REFRESH = "refresh"


class CasePriority(str, Enum):
    """测试用例优先级"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class CaseStatus(str, Enum):
    """测试用例状态"""
    DRAFT = "草稿"
    ACTIVE = "激活"
    DISABLED = "禁用"
    ARCHIVED = "归档"


class TaskStatus(str, Enum):
    """测试单状态"""
    PENDING = "待执行"
    RUNNING = "执行中"
    COMPLETED = "已完成"
    CANCELLED = "已取消"
    FAILED = "执行失败"


class TaskContentType(str, Enum):
    """测试单内容类型"""
    SUITE = "SUITE"
    CASE = "CASE"


class ExecutionStatus(str, Enum):
    """执行状态"""
    PASSED = "通过"
    FAILED = "失败"
    SKIPPED = "跳过"
    INTERRUPTED = "中断"


# ==================== 模型定义 ====================

class TestProductRole(BaseModel, TimestampMixin):
    """产品角色字典表"""
    product = fields.CharField(max_length=100, index=True, description="产品名称")
    role_name = fields.CharField(max_length=100, description="角色名称")
    role_code = fields.CharField(max_length=50, index=True, description="角色编码")
    description = fields.TextField(null=True, description="描述")
    created_by = fields.CharField(max_length=50, description="创建人")

    class Meta(BaseModel.Meta):
        table = "test_product_roles"
        table_description = "产品角色字典表"
        unique_together = (("product", "role_name"),)
        abstract = False


class TestCommonUser(BaseModel, TimestampMixin):
    """测试用户表（被测系统的业务用户）"""
    username = fields.CharField(max_length=100, description="用户名")
    password = fields.CharField(max_length=255, description="密码")
    product = fields.CharField(max_length=100, index=True, description="所属产品/项目")
    role_name = fields.CharField(max_length=100, description="业务角色")
    description = fields.TextField(null=True, description="描述")
    created_by = fields.CharField(max_length=50, description="创建人")

    class Meta(BaseModel.Meta):
        table = "test_common_users"
        table_description = "测试用户表"
        abstract = False


class TestUIElement(BaseModel, TimestampMixin):
    """页面元素表"""
    name = fields.CharField(max_length=100, description="元素名称")
    selector_type = fields.CharEnumField(SelectorType, description="定位器类型")
    selector_value = fields.CharField(max_length=500, description="定位器值")
    description = fields.TextField(null=True, description="元素描述")
    page = fields.CharField(max_length=500, index=True, description="所属页面")
    module = fields.CharField(max_length=100, index=True, null=True, description="所属模块")
    created_by = fields.CharField(max_length=50, description="创建人")

    # 反向关联
    steps: fields.ReverseRelation["TestUIStep"]
    permissions: fields.ReverseRelation["TestUIElementPermission"]

    class Meta(BaseModel.Meta):
        table = "test_ui_elements"
        table_description = "页面元素表"
        abstract = False


class TestUIElementPermission(BaseModel):
    """页面元素权限关联表"""
    element = fields.ForeignKeyField(
        "models.TestUIElement",
        related_name="permissions",
        on_delete=fields.CASCADE,
        description="页面元素ID"
    )
    role_name = fields.CharField(max_length=100, description="测试用户角色")
    created_time = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta(BaseModel.Meta):
        table = "test_ui_element_permissions"
        table_description = "页面元素权限关联表"
        unique_together = (("element", "role_name"),)
        abstract = False


class TestUICase(BaseModel, TimestampMixin):
    """测试用例表"""
    name = fields.CharField(max_length=200, description="用例名称")
    description = fields.TextField(null=True, description="用例描述")
    priority = fields.CharEnumField(CasePriority, default=CasePriority.MEDIUM, index=True, description="优先级")
    module = fields.CharField(max_length=100, index=True, null=True, description="所属模块")
    tags = fields.JSONField(null=True, description="标签数组")
    status = fields.CharEnumField(CaseStatus, default=CaseStatus.DRAFT, index=True, description="状态")
    precondition = fields.TextField(null=True, description="前置条件")
    expected_result = fields.TextField(null=True, description="预期结果")
    created_by = fields.CharField(max_length=50, description="创建人")

    # 反向关联
    steps: fields.ReverseRelation["TestUIStep"]
    permissions: fields.ReverseRelation["TestUICasePermission"]
    suite_relations: fields.ReverseRelation["TestUICasesSuitesRelation"]
    execution_records: fields.ReverseRelation["TestUICaseExecutionRecord"]

    class Meta(BaseModel.Meta):
        table = "test_ui_cases"
        table_description = "测试用例表"
        abstract = False


class TestUICasePermission(BaseModel):
    """测试用例权限关联表"""
    test_case = fields.ForeignKeyField(
        "models.TestUICase",
        related_name="permissions",
        on_delete=fields.CASCADE,
        description="测试用例ID"
    )
    role_name = fields.CharField(max_length=100, description="测试用户角色")
    created_time = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta(BaseModel.Meta):
        table = "test_ui_case_permissions"
        table_description = "测试用例权限关联表"
        unique_together = (("test_case", "role_name"),)
        abstract = False


class TestUIStep(BaseModel):
    """测试步骤表"""
    test_case = fields.ForeignKeyField(
        "models.TestUICase",
        related_name="steps",
        on_delete=fields.CASCADE,
        index=True,
        description="所属测试用例ID"
    )
    step_number = fields.IntField(description="步骤序号")
    action = fields.CharField(max_length=50, description="操作类型")
    element = fields.ForeignKeyField(
        "models.TestUIElement",
        related_name="steps",
        on_delete=fields.SET_NULL,
        null=True,
        description="关联页面元素ID"
    )
    input_data = fields.CharField(max_length=500, null=True, description="输入数据")
    wait_time = fields.IntField(null=True, description="等待时间(毫秒)")
    description = fields.TextField(description="步骤描述")
    sort_order = fields.IntField(default=0, description="排序序号")

    class Meta(BaseModel.Meta):
        table = "test_ui_steps"
        table_description = "测试步骤表"
        abstract = False


class TestUICaseSuite(BaseModel, TimestampMixin):
    """测试套件表"""
    name = fields.CharField(max_length=200, description="套件名称")
    description = fields.TextField(null=True, description="套件描述")
    filter_conditions = fields.JSONField(description="筛选条件")
    created_by = fields.CharField(max_length=50, description="创建人")

    # 反向关联
    case_relations: fields.ReverseRelation["TestUICasesSuitesRelation"]
    task_contents: fields.ReverseRelation["TestUITaskContent"]

    class Meta(BaseModel.Meta):
        table = "test_ui_case_suites"
        table_description = "测试套件表"
        abstract = False


class TestUICasesSuitesRelation(BaseModel):
    """测试套件用例关联表"""
    test_suite = fields.ForeignKeyField(
        "models.TestUICaseSuite",
        related_name="case_relations",
        on_delete=fields.CASCADE,
        index=True,
        description="测试套件ID"
    )
    test_case = fields.ForeignKeyField(
        "models.TestUICase",
        related_name="suite_relations",
        on_delete=fields.CASCADE,
        description="测试用例ID"
    )
    sort_order = fields.IntField(default=0, description="排序序号")
    created_time = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta(BaseModel.Meta):
        table = "test_ui_cases_suites_relation"
        table_description = "测试套件用例关联表"
        unique_together = (("test_suite", "test_case"),)
        abstract = False


class TestUITask(BaseModel):
    """测试单表"""
    name = fields.CharField(max_length=200, description="测试单名称")
    description = fields.TextField(null=True, description="描述")
    environment = fields.CharField(max_length=100, index=True, description="测试环境")
    status = fields.CharEnumField(TaskStatus, default=TaskStatus.PENDING, index=True, description="状态")
    execute_config = fields.JSONField(description="执行配置")
    created_by = fields.CharField(max_length=50, description="创建人")
    created_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    start_time = fields.DatetimeField(null=True, description="开始时间")
    end_time = fields.DatetimeField(null=True, description="结束时间")

    # 反向关联
    contents: fields.ReverseRelation["TestUITaskContent"]
    reports: fields.ReverseRelation["TestUIReport"]

    class Meta(BaseModel.Meta):
        table = "test_ui_tasks"
        table_description = "测试单表"
        abstract = False


class TestUITaskContent(BaseModel):
    """测试单内容表"""
    test_task = fields.ForeignKeyField(
        "models.TestUITask",
        related_name="contents",
        on_delete=fields.CASCADE,
        index=True,
        description="测试单ID"
    )
    item_type = fields.CharEnumField(TaskContentType, description="类型：套件/用例")
    item_id = fields.BigIntField(description="套件ID或用例ID")
    sort_order = fields.IntField(default=0, description="排序序号")

    class Meta(BaseModel.Meta):
        table = "test_ui_task_contents"
        table_description = "测试单内容表"
        abstract = False


class TestUIReport(BaseModel):
    """测试报告表"""
    test_task = fields.ForeignKeyField(
        "models.TestUITask",
        related_name="reports",
        on_delete=fields.CASCADE,
        index=True,
        description="测试单ID"
    )
    execution_time = fields.DatetimeField(index=True, description="执行时间")
    total_cases = fields.IntField(default=0, description="总用例数")
    passed_cases = fields.IntField(default=0, description="通过数")
    failed_cases = fields.IntField(default=0, description="失败数")
    skipped_cases = fields.IntField(default=0, description="跳过数")
    execution_duration = fields.IntField(default=0, description="执行耗时(秒)")
    pass_rate = fields.DecimalField(max_digits=5, decimal_places=2, default=0.00, description="通过率")
    report_data = fields.JSONField(description="详细报告数据")

    # 反向关联
    case_executions: fields.ReverseRelation["TestUICaseExecutionRecord"]

    class Meta(BaseModel.Meta):
        table = "test_ui_reports"
        table_description = "测试报告表"
        abstract = False


class TestUICaseExecutionRecord(BaseModel):
    """用例执行记录表"""
    test_case = fields.ForeignKeyField(
        "models.TestUICase",
        related_name="execution_records",
        on_delete=fields.CASCADE,
        index=True,
        description="测试用例ID"
    )
    test_report = fields.ForeignKeyField(
        "models.TestUIReport",
        related_name="case_executions",
        on_delete=fields.CASCADE,
        index=True,
        description="测试报告ID"
    )
    status = fields.CharEnumField(ExecutionStatus, description="执行状态")
    start_time = fields.DatetimeField(description="开始时间")
    end_time = fields.DatetimeField(description="结束时间")
    duration = fields.IntField(default=0, description="耗时(秒)")
    error_message = fields.TextField(null=True, description="错误信息")
    screenshot_path = fields.CharField(max_length=500, null=True, description="截图路径")

    # 反向关联
    step_executions: fields.ReverseRelation["TestUICaseStepExecutionRecord"]

    class Meta(BaseModel.Meta):
        table = "test_ui_case_execution_records"
        table_description = "用例执行记录表"
        abstract = False


class TestUICaseStepExecutionRecord(BaseModel):
    """用例步骤执行记录表"""
    case_execution_record = fields.ForeignKeyField(
        "models.TestUICaseExecutionRecord",
        related_name="step_executions",
        on_delete=fields.CASCADE,
        index=True,
        description="用例执行记录ID"
    )
    step_number = fields.IntField(description="步骤序号")
    action = fields.CharField(max_length=50, description="操作类型")
    element = fields.ForeignKeyField(
        "models.TestUIElement",
        on_delete=fields.SET_NULL,
        null=True,
        description="关联页面元素ID"
    )
    input_data = fields.CharField(max_length=500, null=True, description="输入数据")
    status = fields.CharEnumField(ExecutionStatus, max_length=10, description="步骤执行状态")
    start_time = fields.DatetimeField(description="开始时间")
    end_time = fields.DatetimeField(description="结束时间")
    duration = fields.IntField(default=0, description="耗时(毫秒)")
    error_message = fields.TextField(null=True, description="错误信息")
    screenshot_path = fields.CharField(max_length=500, null=True, description="截图路径")

    class Meta(BaseModel.Meta):
        table = "test_ui_case_step_execution_records"
        table_description = "用例步骤执行记录表"
        abstract = False
