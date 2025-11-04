# UI自动化测试平台需求规格说明书
## 一、核心功能模块
1. 测试用户管理模块：管理被测系统的用户角色与账号信息。
2. 页面元素维护模块：维护所有被测页面的UI元素定位信息。
3. 测试用例管理模块：编写和管理自动化测试用例。
4. 测试套件管理模块：通过动态筛选条件组合测试用例集合。
5. 测试单管理模块：创建和执行测试任务，管理执行策略。
6. 测试报告与历史报告模块：查看、分析和对比测试执行结果。
## 二、功能模块详细描述
### 1. 测试用户管理模块
功能：管理不同产品或环境下的业务用户账号，供测试用例在执行时使用。
- 用户列表：
  - 搜索框（按用户名、产品/项目搜索）。
  - 用户表格（用户名、密码（加密显示）、所属产品/项目、角色、操作）。
- 用户编辑/新增表单：
  - 用户名输入框。
  - 密码输入框（支持明文/密文切换显示）。
  - 所属产品/项目选择器。
  - 业务角色选择器（如：普通会员、VIP会员、商家）。
- 权限关联：
  - 提供功能入口，可将特定“测试用户角色”与“页面元素”或“测试用例”关联，用于标识拥有该业务角色的用户才能操作相关元素或执行相关用例的场景。
### 2. 页面元素维护模块
功能：维护所有页面元素信息，支持权限控制。
页面内容：
- 元素列表
  - 搜索框（按元素名称、页面URL搜索）
  - 筛选器（按模块、定位器类型筛选）
  - 元素表格（名称、定位器、页面URL、操作）
  - 批量操作按钮
- 元素编辑/新增表单
  - 元素名称输入框
  - 定位器类型选择器（ID/Name/CSS/XPath/Class/Test-ID）
  - 定位器值输入框
  - 所属页面输入框
  - 所属模块输入框
  - 元素描述文本框
- 关联查看：
  - 点击关联用例按钮跳转到测试用例列表页面，并自动筛选测试步骤中引用了该元素的相关测试用例列表。
  - 查看关联的权限角色列表，即哪些业务角色有权限操作此元素。
### 3. 测试用例管理模块
功能一：编写和维护测试用例，支持权限控制
页面内容：
- 用例列表
  - 高级搜索（名称、模块、优先级、标签）
  - 用例表格（名称、优先级、状态（草稿/激活/禁用）、创建人、操作）
  - 批量操作：启用/禁用/复制/删除
- 用例编辑/新增
  - 基本信息区域（名称、描述、优先级、模块、标签）
  - 前置条件输入框
  - 预期结果输入框
- 测试步骤编辑区域
  - 步骤列表（拖拽排序）
  - 每步包含：操作类型选择、元素选择、输入数据、等待时间、描述
  - 步骤复制/删除功能
- 关联查看：
  - 查看关联的元素列表
  - 查看关联的权限角色列表，即哪些测试用户角色可以执行此用例
  - 查看历史执行记录侧边栏（时间、结果、报告链接）
功能二：查看单个测试用例的所有历史执行记录
页面内容：
- 用例基本信息头
  - 用例名称、描述
  - 当前状态、优先级
- 历史执行记录表格
  - 执行时间
  - 所属测试单
  - 执行结果状态
  - 执行耗时
  - 错误信息（如有）
  - 操作（查看详情）
- 执行趋势图表
  - 成功率趋势线
  - 平均执行时间变化
  - 失败原因分布
### 4. 测试套件管理模块
功能：通过筛选条件创建和管理测试套件
页面内容：
- 套件列表
  - 套件卡片/列表（名称、用例数量、创建人）
  - 新建套件按钮
- 套件编辑/新增
  - 套件基本信息（名称、描述）
  - 动态筛选条件构建器
    - 模块筛选
    - 优先级筛选
    - 标签筛选
    - 创建人筛选
  - 实时显示匹配的用例数量
  - 匹配用例预览列表
- 套件用例管理
  - 从筛选结果中手动添加/移除用例
  - 用例排序功能
### 5. 测试单管理模块
功能：组合测试套件和用例形成测试任务，配置执行策略
页面内容：
- 测试单列表
  - 状态筛选（待执行/执行中/已完成）
  - 测试单表格（名称、环境、状态、进度、创建人、操作）
  - 新建测试单按钮
- 测试单编辑/新增
  - 基本信息（名称、描述、测试环境）
  - 执行配置：
    - 浏览器类型
    - 超时时间
    - 失败后是否继续执行
    - 失败用例重试次数
    - 失败时自动截图
- 测试内容选择区域
  - 测试套件选择标签页
  - 测试用例选择标签页
  - 已选内容展示（可移除、可调整顺序）
  - 执行进度显示，根据你已执行用例数量与未执行用例数量显示测试单整体执行进度
  - 预计执行时间估算，根据测试单用例的历史执行时间汇总估算执行时间和剩余时间
- 测试单操作
  - 立即执行按钮
  - 定时执行设置
  - 执行历史快速查看
6. 测试报告查看模块
主要功能：查看测试执行结果和历史报告
页面内容：
- 报告列表
  - 按时间范围筛选
  - 报告卡片（测试单名称、执行时间、通过率、状态）
  - 报告对比功能
- 报告详情页
  - 概览面板
    - 通过率环形图
    - 统计数字（总用例数、通过、失败、跳过）
    - 执行时长、开始结束时间
    - 环境信息
  - 用例执行详情
    - 状态筛选（全部/通过/失败/跳过）
    - 用例执行列表（用例名称、状态、耗时、错误信息）
    - 点击查看单个用例执行详情
  - 失败分析
    - 失败用例分类统计
    - 常见错误类型分析
    - 失败趋势图表
- 历史报告对比
  - 多份报告并行对比
  - 通过率趋势图
  - 失败用例变化分析
## 三、建表语句
```
-- 测试用户表 (被测系统用户)
CREATE TABLE IF NOT EXISTS test_common_users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    username VARCHAR ( 100 ) NOT NULL COMMENT '用户名',
    PASSWORD VARCHAR ( 255 ) NOT NULL COMMENT '密码',
    product VARCHAR ( 100 ) NOT NULL COMMENT '所属产品/项目',
    role_name VARCHAR ( 100 ) NOT NULL COMMENT '业务角色',
    description TEXT COMMENT '描述',
    created_by VARCHAR ( 50 ) NOT NULL COMMENT '创建人',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_product ( product ) 
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '测试用户表';

-- 页面元素表
CREATE TABLE IF NOT EXISTS test_ui_elements (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    NAME VARCHAR ( 100 ) NOT NULL COMMENT '元素名称',
    selector_type ENUM ( 'ID', 'NAME', 'CSS', 'XPATH', 'CLASS_NAME', 'TAG_NAME', 'LINK_TEXT', 'PARTIAL_LINK_TEXT', 'TEST_ID' ) NOT NULL COMMENT '定位器类型',
    selector_value VARCHAR ( 500 ) NOT NULL COMMENT '定位器值',
    description TEXT COMMENT '元素描述',
    page VARCHAR ( 500 ) NOT NULL COMMENT '所属页面',
    module VARCHAR ( 100 ) COMMENT '所属模块',
    created_by VARCHAR ( 50 ) NOT NULL COMMENT '创建人',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_page ( page ),
    INDEX idx_module ( module )
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '页面元素表';

-- 页面元素权限关联表
CREATE TABLE IF NOT EXISTS test_ui_element_permissions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    element_id BIGINT NOT NULL COMMENT '页面元素ID',
    test_user_role VARCHAR ( 100 ) NOT NULL COMMENT '测试用户角色',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_element_role ( element_id, test_user_role ),
    FOREIGN KEY ( element_id ) REFERENCES test_ui_elements ( id ) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '页面元素权限关联表';

-- 测试用例表
CREATE TABLE IF NOT EXISTS test_ui_cases (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    NAME VARCHAR ( 200 ) NOT NULL COMMENT '用例名称',
    description TEXT COMMENT '用例描述',
    priority ENUM ( '高', '中', '低' ) NOT NULL DEFAULT '中' COMMENT '优先级',
    module VARCHAR ( 100 ) COMMENT '所属模块',
    tags JSON COMMENT '标签数组',
    STATUS ENUM ( '草稿', '激活', '禁用', '归档' ) NOT NULL DEFAULT '草稿' COMMENT '状态',
    precondition TEXT COMMENT '前置条件',
    expected_result TEXT COMMENT '预期结果',
    created_by VARCHAR ( 50 ) NOT NULL COMMENT '创建人',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_priority ( priority ),
    INDEX idx_status ( STATUS ),
    INDEX idx_module ( module )
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '测试用例表';

-- 测试用例权限关联表
CREATE TABLE IF NOT EXISTS test_ui_case_permissions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    test_case_id BIGINT NOT NULL COMMENT '测试用例ID',
    test_user_role VARCHAR ( 100 ) NOT NULL COMMENT '测试用户角色',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_case_role ( test_case_id, test_user_role ),
    FOREIGN KEY ( test_case_id ) REFERENCES test_ui_cases ( id ) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '测试用例权限关联表';

-- 测试步骤表
CREATE TABLE IF NOT EXISTS test_ui_steps (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    test_case_id BIGINT NOT NULL COMMENT '所属测试用例ID',
    step_number INT NOT NULL COMMENT '步骤序号',
    action VARCHAR ( 50 ) NOT NULL COMMENT '操作类型',
    element_id BIGINT COMMENT '关联页面元素ID',
    input_data VARCHAR ( 500 ) COMMENT '输入数据',
    wait_time INT COMMENT '等待时间(毫秒)',
    description TEXT NOT NULL COMMENT '步骤描述',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序序号',
    INDEX idx_test_case_id ( test_case_id ),
    FOREIGN KEY ( test_case_id ) REFERENCES test_ui_cases ( id ) ON DELETE CASCADE,
    FOREIGN KEY ( element_id ) REFERENCES test_ui_elements ( id ) ON DELETE
SET NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '测试步骤表';

-- 测试套件表
CREATE TABLE IF NOT EXISTS test_ui_case_suites (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    NAME VARCHAR ( 200 ) NOT NULL COMMENT '套件名称',
    description TEXT COMMENT '套件描述',
    filter_conditions JSON NOT NULL COMMENT '筛选条件',
    created_by VARCHAR ( 50 ) NOT NULL COMMENT '创建人',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '测试套件表';

-- 测试套件用例关联表
CREATE TABLE IF NOT EXISTS test_ui_cases_suites_relation (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    test_suite_id BIGINT NOT NULL COMMENT '测试套件ID',
    test_case_id BIGINT NOT NULL COMMENT '测试用例ID',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序序号',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_suite_case ( test_suite_id, test_case_id ),
    INDEX idx_test_suite_id ( test_suite_id ),
    FOREIGN KEY ( test_suite_id ) REFERENCES test_ui_case_suites ( id ) ON DELETE CASCADE,
    FOREIGN KEY ( test_case_id ) REFERENCES test_ui_cases ( id ) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '测试套件用例关联表';

-- 测试单表
CREATE TABLE IF NOT EXISTS test_ui_tasks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    NAME VARCHAR ( 200 ) NOT NULL COMMENT '测试单名称',
    description TEXT COMMENT '描述',
    environment VARCHAR ( 100 ) NOT NULL COMMENT '测试环境',
    STATUS ENUM ( '待执行', '执行中', '已完成', '已取消', '执行失败' ) NOT NULL DEFAULT '待执行' COMMENT '状态',
    execute_config JSON NOT NULL COMMENT '执行配置',
    created_by VARCHAR ( 50 ) NOT NULL COMMENT '创建人',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    start_time DATETIME COMMENT '开始时间',
    end_time DATETIME COMMENT '结束时间',
    INDEX idx_status ( STATUS ),
    INDEX idx_environment ( environment )
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '测试单表';

-- 测试单内容表
CREATE TABLE IF NOT EXISTS test_ui_task_contents (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    test_task_id BIGINT NOT NULL COMMENT '测试单ID',
    item_type ENUM ( 'SUITE', 'CASE' ) NOT NULL COMMENT '类型：套件/用例',
    item_id BIGINT NOT NULL COMMENT '套件ID或用例ID',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序序号',
    INDEX idx_test_task_id ( test_task_id ),
    FOREIGN KEY ( test_task_id ) REFERENCES test_ui_tasks ( id ) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '测试单内容表';

-- 测试报告表
CREATE TABLE IF NOT EXISTS test_ui_reports (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    test_task_id BIGINT NOT NULL COMMENT '测试单ID',
    execution_time DATETIME NOT NULL COMMENT '执行时间',
    total_cases INT NOT NULL DEFAULT 0 COMMENT '总用例数',
    passed_cases INT NOT NULL DEFAULT 0 COMMENT '通过数',
    failed_cases INT NOT NULL DEFAULT 0 COMMENT '失败数',
    skipped_cases INT NOT NULL DEFAULT 0 COMMENT '跳过数',
    execution_duration INT NOT NULL DEFAULT 0 COMMENT '执行耗时(秒)',
    pass_rate DECIMAL ( 5, 2 ) NOT NULL DEFAULT 0.00 COMMENT '通过率',
    report_data JSON NOT NULL COMMENT '详细报告数据',
    INDEX idx_test_task_id ( test_task_id ),
    INDEX idx_execution_time ( execution_time ),
    FOREIGN KEY ( test_task_id ) REFERENCES test_ui_tasks ( id ) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '测试报告表';

-- 用例执行记录表
CREATE TABLE IF NOT EXISTS test_ui_case_execution_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    test_case_id BIGINT NOT NULL COMMENT '测试用例ID',
    test_report_id BIGINT NOT NULL COMMENT '测试报告ID',
    STATUS ENUM ( '通过', '失败', '跳过', '中断' ) NOT NULL COMMENT '执行状态',
    start_time DATETIME NOT NULL COMMENT '开始时间',
    end_time DATETIME NOT NULL COMMENT '结束时间',
    duration INT NOT NULL DEFAULT 0 COMMENT '耗时(秒)',
    error_message TEXT COMMENT '错误信息',
    screenshot_path VARCHAR ( 500 ) COMMENT '截图路径',
    INDEX idx_test_case_id ( test_case_id ),
    INDEX idx_test_report_id ( test_report_id ),
    FOREIGN KEY ( test_case_id ) REFERENCES test_ui_cases ( id ) ON DELETE CASCADE,
    FOREIGN KEY ( test_report_id ) REFERENCES test_ui_reports ( id ) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '用例执行记录表';

-- 用例步骤执行记录表
CREATE TABLE IF NOT EXISTS test_ui_case_step_execution_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    case_execution_record_id BIGINT NOT NULL COMMENT '用例执行记录ID',
    step_number INT NOT NULL COMMENT '步骤序号',
    action VARCHAR ( 50 ) NOT NULL COMMENT '操作类型',
    element_id BIGINT COMMENT '关联页面元素ID',
    input_data VARCHAR ( 500 ) COMMENT '输入数据',
    STATUS ENUM ( '通过', '失败', '跳过' ) NOT NULL COMMENT '步骤执行状态',
    start_time DATETIME NOT NULL COMMENT '开始时间',
    end_time DATETIME NOT NULL COMMENT '结束时间',
    duration INT NOT NULL DEFAULT 0 COMMENT '耗时(毫秒)',
    error_message TEXT COMMENT '错误信息',
    screenshot_path VARCHAR ( 500 ) COMMENT '截图路径',
    INDEX idx_case_execution_record_id ( case_execution_record_id ),
    FOREIGN KEY ( case_execution_record_id ) REFERENCES test_ui_case_execution_records ( id ) ON DELETE CASCADE,
    FOREIGN KEY ( element_id ) REFERENCES test_ui_elements ( id ) ON DELETE
SET NULL 
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '用例步骤执行记录表';
```

