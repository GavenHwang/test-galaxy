"""
UI自动化测试平台 - Schema定义
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


# ==================== 基础Schema ====================

class BaseResponseSchema(BaseModel):
    """基础响应Schema"""
    id: int
    created_time: str
    updated_time: str

    class Config:
        from_attributes = True


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页条数")


class PaginatedResponse(BaseModel):
    """分页响应"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int


# ==================== 产品管理 Schema ====================

class ProductCreateSchema(BaseModel):
    """创建产品请求"""
    name: str = Field(..., min_length=1, max_length=100, description="产品名称")
    code: Optional[str] = Field(None, max_length=50, description="产品编码")
    status: str = Field(default="ENABLED", description="状态")
    sort_order: Optional[int] = Field(0, description="排序序号")
    description: Optional[str] = Field(None, max_length=500, description="描述")


class ProductUpdateSchema(BaseModel):
    """更新产品请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="产品名称")
    code: Optional[str] = Field(None, max_length=50, description="产品编码")
    status: Optional[str] = Field(None, description="状态")
    sort_order: Optional[int] = Field(None, description="排序序号")
    description: Optional[str] = Field(None, max_length=500, description="描述")


class ProductResponseSchema(BaseResponseSchema):
    """产品响应"""
    name: str
    code: Optional[str] = None
    status: str
    sort_order: int
    description: Optional[str] = None
    created_by: str


class ProductListParams(PaginationParams):
    """产品列表查询参数"""
    name: Optional[str] = Field(None, description="产品名称模糊搜索")
    status: Optional[str] = Field(None, description="状态")


class ProductStatusUpdateSchema(BaseModel):
    """产品状态更新请求"""
    status: str = Field(..., description="新状态")


# ==================== 测试用户 Schema ====================

class TestUserCreateSchema(BaseModel):
    """创建测试用户请求"""
    username: str = Field(..., min_length=2, max_length=100, description="用户名")
    password: str = Field(..., min_length=6, max_length=255, description="密码")
    product: str = Field(..., min_length=1, max_length=100, description="所属产品/项目")
    role_name: str = Field(..., min_length=1, max_length=100, description="业务角色")
    role_code: str = Field(..., min_length=1, max_length=50, description="角色编码")
    description: Optional[str] = Field(None, max_length=500, description="描述")


class TestUserUpdateSchema(BaseModel):
    """更新测试用户请求"""
    username: Optional[str] = Field(None, min_length=2, max_length=100, description="用户名")
    password: Optional[str] = Field(None, min_length=6, max_length=255, description="密码")
    product: Optional[str] = Field(None, min_length=1, max_length=100, description="所属产品/项目")
    role_name: Optional[str] = Field(None, min_length=1, max_length=100, description="业务角色")
    role_code: Optional[str] = Field(None, min_length=1, max_length=50, description="角色编码")
    description: Optional[str] = Field(None, max_length=500, description="描述")


class TestUserResponseSchema(BaseResponseSchema):
    """测试用户响应"""
    username: str
    password: str  # 前端显示时需要处理为******
    product: str
    role_name: str
    role_code: Optional[str] = None
    description: Optional[str] = None
    created_by: str


class TestUserListParams(PaginationParams):
    """测试用户列表查询参数"""
    username: Optional[str] = Field(None, description="用户名模糊搜索")
    product: Optional[str] = Field(None, description="产品名称")
    role_name: Optional[str] = Field(None, description="角色名称")


# ==================== 页面元素 Schema ====================

class UIElementCreateSchema(BaseModel):
    """创建页面元素请求"""
    name: str = Field(..., min_length=1, max_length=100, description="元素名称")
    selector_type: str = Field(..., description="定位器类型")
    selector_value: str = Field(..., min_length=1, max_length=500, description="定位器值")
    description: Optional[str] = Field(None, max_length=1000, description="元素描述")
    page: str = Field(..., min_length=1, max_length=500, description="所属页面")
    module: Optional[str] = Field(None, max_length=100, description="所属模块")


class UIElementUpdateSchema(BaseModel):
    """更新页面元素请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="元素名称")
    selector_type: Optional[str] = Field(None, description="定位器类型")
    selector_value: Optional[str] = Field(None, min_length=1, max_length=500, description="定位器值")
    description: Optional[str] = Field(None, max_length=1000, description="元素描述")
    page: Optional[str] = Field(None, min_length=1, max_length=500, description="所属页面")
    module: Optional[str] = Field(None, max_length=100, description="所属模块")


class UIElementResponseSchema(BaseResponseSchema):
    """页面元素响应"""
    name: str
    selector_type: str
    selector_value: str
    description: Optional[str] = None
    page: str
    module: Optional[str] = None
    created_by: str
    related_cases_count: Optional[int] = 0
    permission_roles: Optional[List[str]] = []


class UIElementListParams(PaginationParams):
    """页面元素列表查询参数"""
    name: Optional[str] = Field(None, description="元素名称模糊搜索")
    page: Optional[str] = Field(None, description="所属页面")
    module: Optional[str] = Field(None, description="所属模块")
    selector_type: Optional[str] = Field(None, description="定位器类型")


class UIElementBatchCreateSchema(BaseModel):
    """批量创建页面元素请求"""
    elements: List[UIElementCreateSchema]


class ElementPermissionSchema(BaseModel):
    """元素权限设置请求"""
    roles: List[str] = Field(..., description="角色数组")


# ==================== 测试用例 Schema ====================

class TestStepSchema(BaseModel):
    """测试步骤Schema"""
    id: Optional[int] = None
    step_number: int = Field(..., description="步骤序号")
    action: str = Field(..., description="操作类型")
    element_id: Optional[int] = Field(None, description="关联页面元素ID")
    input_data: Optional[str] = Field(None, max_length=500, description="输入数据")
    wait_time: Optional[int] = Field(None, ge=0, le=60000, description="等待时间(毫秒)")
    description: str = Field(..., min_length=1, max_length=500, description="步骤描述")
    sort_order: int = Field(default=0, description="排序序号")


class TestStepCreateSchema(BaseModel):
    """创建测试步骤请求"""
    step_number: int = Field(..., description="步骤序号")
    action: str = Field(..., description="操作类型")
    element_id: Optional[int] = Field(None, description="关联页面元素ID")
    input_data: Optional[str] = Field(None, max_length=500, description="输入数据")
    wait_time: Optional[int] = Field(None, ge=0, le=60000, description="等待时间(毫秒)")
    description: str = Field(..., min_length=1, max_length=500, description="步骤描述")
    sort_order: int = Field(default=0, description="排序序号")


class TestStepUpdateSchema(BaseModel):
    """更新测试步骤请求"""
    step_number: Optional[int] = Field(None, description="步骤序号")
    action: Optional[str] = Field(None, description="操作类型")
    element_id: Optional[int] = Field(None, description="关联页面元素ID")
    input_data: Optional[str] = Field(None, max_length=500, description="输入数据")
    wait_time: Optional[int] = Field(None, ge=0, le=60000, description="等待时间(毫秒)")
    description: Optional[str] = Field(None, min_length=1, max_length=500, description="步骤描述")
    sort_order: Optional[int] = Field(None, description="排序序号")


class TestStepResponseSchema(BaseModel):
    """测试步骤响应"""
    id: int
    test_case_id: int
    step_number: int
    action: str
    element_id: Optional[int] = None
    input_data: Optional[str] = None
    wait_time: Optional[int] = None
    description: str
    sort_order: int


class TestCaseCreateSchema(BaseModel):
    """创建测试用例请求"""
    name: str = Field(..., min_length=1, max_length=200, description="用例名称")
    description: Optional[str] = Field(None, max_length=2000, description="用例描述")
    priority: str = Field(default="中", description="优先级")
    module: Optional[str] = Field(None, max_length=100, description="所属模块")
    tags: Optional[List[str]] = Field(None, description="标签数组")
    status: str = Field(default="草稿", description="状态")
    precondition: Optional[str] = Field(None, max_length=1000, description="前置条件")
    expected_result: Optional[str] = Field(None, max_length=1000, description="预期结果")
    steps: Optional[List[TestStepSchema]] = Field(None, description="测试步骤")


class TestCaseUpdateSchema(BaseModel):
    """更新测试用例请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="用例名称")
    description: Optional[str] = Field(None, max_length=2000, description="用例描述")
    priority: Optional[str] = Field(None, description="优先级")
    module: Optional[str] = Field(None, max_length=100, description="所属模块")
    tags: Optional[List[str]] = Field(None, description="标签数组")
    status: Optional[str] = Field(None, description="状态")
    precondition: Optional[str] = Field(None, max_length=1000, description="前置条件")
    expected_result: Optional[str] = Field(None, max_length=1000, description="预期结果")


class TestCaseResponseSchema(BaseResponseSchema):
    """测试用例响应"""
    name: str
    description: Optional[str] = None
    priority: str
    module: Optional[str] = None
    product: str
    tags: Optional[List[str]] = None
    status: str
    precondition: Optional[str] = None
    expected_result: Optional[str] = None
    created_by: str
    steps: Optional[List[TestStepResponseSchema]] = None  # 修改为TestStepResponseSchema
    permission_roles: Optional[List[str]] = []
    execution_count: Optional[int] = 0
    last_execution_status: Optional[str] = None
    last_execution_time: Optional[str] = None


class TestCaseListParams(PaginationParams):
    """测试用例列表查询参数"""
    name: Optional[str] = Field(None, description="用例名称模糊搜索")
    module: Optional[str] = Field(None, description="所属模块")
    priority: Optional[str] = Field(None, description="优先级")
    status: Optional[str] = Field(None, description="状态")
    tags: Optional[str] = Field(None, description="标签，逗号分隔")
    created_by: Optional[str] = Field(None, description="创建人")
    product: Optional[str] = Field(None, description="所属产品")


class CasePermissionSchema(BaseModel):
    """用例权限设置请求"""
    roles: List[str] = Field(..., description="角色数组")


class StepReorderSchema(BaseModel):
    """步骤重排序请求"""
    step_ids: List[int] = Field(..., description="步骤ID数组（新顺序）")


class CaseStatusUpdateSchema(BaseModel):
    """用例状态更新请求"""
    status: str = Field(..., description="新状态")


class BatchUpdateStatusSchema(BaseModel):
    """批量更新状态请求"""
    case_ids: List[int] = Field(..., description="用例ID数组")
    status: str = Field(..., description="新状态")


# ==================== 测试套件 Schema ====================

class TestSuiteFilterConditions(BaseModel):
    """测试套件筛选条件"""
    module: Optional[List[str]] = None
    priority: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: Optional[List[str]] = None
    created_by: Optional[List[str]] = None


class TestSuiteCreateSchema(BaseModel):
    """创建测试套件请求"""
    name: str = Field(..., min_length=1, max_length=200, description="套件名称")
    description: Optional[str] = Field(None, max_length=2000, description="套件描述")
    product: str = Field(..., min_length=1, max_length=100, description="所属产品")
    filter_conditions: TestSuiteFilterConditions = Field(..., description="筛选条件")


class TestSuiteUpdateSchema(BaseModel):
    """更新测试套件请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="套件名称")
    description: Optional[str] = Field(None, max_length=2000, description="套件描述")
    product: Optional[str] = Field(None, min_length=1, max_length=100, description="所属产品")
    filter_conditions: Optional[TestSuiteFilterConditions] = Field(None, description="筛选条件")


class TestSuiteResponseSchema(BaseResponseSchema):
    """测试套件响应"""
    name: str
    description: Optional[str] = None
    product: str
    filter_conditions: Dict[str, Any]
    created_by: str
    case_count: int = 0
    cases: Optional[List[TestCaseResponseSchema]] = None


class TestSuiteListParams(PaginationParams):
    """测试套件列表查询参数"""
    name: Optional[str] = Field(None, description="套件名称模糊搜索")
    created_by: Optional[str] = Field(None, description="创建人")
    product: Optional[str] = Field(None, description="所属产品")


class AddCasesToSuiteSchema(BaseModel):
    """添加用例到套件请求"""
    case_ids: List[int] = Field(..., description="用例ID数组")


class CaseReorderSchema(BaseModel):
    """用例重排序请求"""
    case_ids: List[int] = Field(..., description="用例ID数组（新顺序）")


# ==================== 测试单 Schema ====================

class ExecuteConfigSchema(BaseModel):
    """执行配置Schema"""
    browser: str = Field(default="chromium", description="浏览器类型")
    timeout: int = Field(default=30000, description="超时时间(毫秒)")
    continue_on_failure: bool = Field(default=True, description="失败后是否继续")
    retry_count: int = Field(default=2, ge=0, le=5, description="失败重试次数")
    auto_screenshot: bool = Field(default=True, description="失败时自动截图")


class TaskContentSchema(BaseModel):
    """测试单内容Schema"""
    item_type: str = Field(..., description="类型：SUITE/CASE")
    item_id: int = Field(..., description="套件ID或用例ID")
    sort_order: int = Field(default=0, description="排序序号")


class TestTaskCreateSchema(BaseModel):
    """创建测试单请求"""
    name: str = Field(..., min_length=1, max_length=200, description="测试单名称")
    description: Optional[str] = Field(None, max_length=2000, description="描述")
    product: str = Field(..., min_length=1, max_length=100, description="所属产品")
    environment: str = Field(..., min_length=1, max_length=100, description="测试环境")
    execute_config: dict = Field(..., description="执行配置")
    suites: Optional[List[int]] = Field(default=[], description="套件ID列表")
    cases: Optional[List[int]] = Field(default=[], description="用例ID列表")


class TestTaskUpdateSchema(BaseModel):
    """更新测试单请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="测试单名称")
    description: Optional[str] = Field(None, max_length=2000, description="描述")
    product: Optional[str] = Field(None, min_length=1, max_length=100, description="所属产品")
    environment: Optional[str] = Field(None, min_length=1, max_length=100, description="测试环境")
    execute_config: Optional[dict] = Field(None, description="执行配置")
    suites: Optional[List[int]] = Field(None, description="套件ID列表")
    cases: Optional[List[int]] = Field(None, description="用例ID列表")


class TestTaskResponseSchema(BaseResponseSchema):
    """测试单响应"""
    name: str
    description: Optional[str] = None
    product: str
    environment: str
    status: str
    execute_config: Dict[str, Any]
    created_by: str
    created_time: str
    updated_time: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    total_cases: int = 0
    executed_cases: int = 0
    passed_cases: int = 0
    failed_cases: int = 0
    progress: Optional[float] = 0.0
    estimated_time: Optional[int] = None
    suites: Optional[List[int]] = []  # 已选择的套件ID列表
    cases: Optional[List[int]] = []   # 已选择的用例ID列表


class TestTaskListParams(PaginationParams):
    """测试单列表查询参数"""
    name: Optional[str] = Field(None, description="测试单名称模糊搜索")
    status: Optional[str] = Field(None, description="状态")
    environment: Optional[str] = Field(None, description="测试环境")
    product: Optional[str] = Field(None, description="所属产品")


# ==================== 测试报告 Schema ====================

class CaseExecutionRecordSchema(BaseModel):
    """用例执行记录Schema"""
    id: int
    test_case_id: int
    test_case_name: Optional[str] = None
    status: str
    start_time: str
    end_time: str
    duration: int
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None


class TestReportResponseSchema(BaseResponseSchema):
    """测试报告响应"""
    test_task_id: int
    product: str
    execution_time: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    skipped_cases: int
    execution_duration: int
    pass_rate: Decimal
    report_data: Dict[str, Any]
    case_executions: Optional[List[CaseExecutionRecordSchema]] = None


class TestReportListParams(PaginationParams):
    """测试报告列表查询参数"""
    test_task_id: Optional[int] = Field(None, description="测试单ID")
    start_date: Optional[str] = Field(None, description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")
    product: Optional[str] = Field(None, description="所属产品")


class ReportCompareSchema(BaseModel):
    """报告对比请求"""
    report_ids: List[int] = Field(..., min_items=2, max_items=5, description="报告ID数组（2-5个）")


# ==================== 执行历史 Schema ====================

class ExecutionHistorySchema(BaseModel):
    """执行历史Schema"""
    id: int
    test_case_id: int
    test_report_id: int
    test_task_name: Optional[str] = None
    status: str
    start_time: str
    end_time: str
    duration: int
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None


class ExecutionTrendData(BaseModel):
    """执行趋势数据"""
    pass_rate_trend: List[Dict[str, Any]] = []
    avg_duration_trend: List[Dict[str, Any]] = []
    failure_reasons: Dict[str, int] = {}
