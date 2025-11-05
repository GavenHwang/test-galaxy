# 修复测试用例API中的Pydantic验证错误

## 需求概述

修复测试用例创建、更新等API接口中出现的Pydantic验证错误。当前错误提示显示 `created_time` 和 `updated_time` 字段类型不匹配：Schema定义为字符串类型，但后端传入了datetime对象。

## 问题分析

### 错误现象

调用测试用例创建API时，前端收到如下错误响应：

```
2 validation errors for TestCaseResponseSchema
created_time Input should be a valid string [type=string_type, input_value=datetime.datetime(...), input_type=datetime]
updated_time Input should be a valid string [type=string_type, input_value=datetime.datetime(...), input_type=datetime]
```

### 根本原因

在 `backend/app/schemas/ui_test.py` 中，`BaseResponseSchema` 定义了时间字段为字符串类型：

```
class BaseResponseSchema(BaseModel):
    id: int
    created_time: str
    updated_time: str
```

但在 `backend/app/api/ui_test_case.py` 的多个API接口中，直接将模型的datetime对象传递给Schema构造器：

```
case_data = TestCaseResponseSchema(
    ...
    created_time=test_case.created_time,  # datetime对象
    updated_time=test_case.updated_time,  # datetime对象
    ...
)
```

### 影响范围

该问题影响以下API接口的响应数据构造：

1. 创建测试用例：`POST /api/ui-test-cases`
2. 获取测试用例列表：`GET /api/ui-test-cases`
3. 获取测试用例详情：`GET /api/ui-test-cases/{case_id}`
4. 更新测试用例：`PUT /api/ui-test-cases/{case_id}`
5. 复制测试用例：`POST /api/ui-test-cases/{case_id}/copy`

所有构造 `TestCaseResponseSchema` 的地方都受影响。

## 解决方案

### 方案选择

提供两种可选方案：

**方案一：修改Schema定义（推荐）**

将 `BaseResponseSchema` 的时间字段类型改为 `datetime`，利用Pydantic的自动序列化能力。

优点：
- 类型安全，符合Python最佳实践
- Pydantic自动处理序列化，输出JSON时自动转换为ISO 8601字符串
- 无需手动转换，减少代码重复
- 统一所有使用 `BaseResponseSchema` 的Schema

缺点：
- 需要验证前端是否能正确解析ISO 8601格式

**方案二：在API层手动转换**

保持Schema定义不变，在每个API接口构造响应时将datetime转换为字符串。

优点：
- Schema定义明确为字符串
- 可控制时间格式

缺点：
- 需要修改多处代码
- 容易遗漏新增接口
- 代码重复度高

### 最终方案

采用**方案一**，理由如下：
- Pydantic 2.x版本推荐使用原生类型，自动处理序列化
- 减少代码维护成本
- 符合FastAPI框架最佳实践

## 设计细节

### Schema修改

修改 `backend/app/schemas/ui_test.py` 中的 `BaseResponseSchema`：

| 字段 | 修改前类型 | 修改后类型 | 说明 |
|------|-----------|-----------|------|
| created_time | str | datetime | 创建时间，序列化为ISO 8601格式 |
| updated_time | str | datetime | 更新时间，序列化为ISO 8601格式 |

同时，所有继承或使用时间字段的Schema中，时间相关字段统一使用 `datetime` 或 `Optional[datetime]` 类型：

- `TestCaseResponseSchema.last_execution_time`：改为 `Optional[datetime]`
- 其他Schema中的时间字段参照执行

### API层调整

由于Schema类型已修改为datetime，API层无需转换，直接传递模型的datetime字段即可。现有代码无需修改，保持当前逻辑：

```
case_data = TestCaseResponseSchema(
    ...
    created_time=test_case.created_time,  # datetime对象，Pydantic自动序列化
    updated_time=test_case.updated_time,  # datetime对象，Pydantic自动序列化
    ...
)
```

### 数据库模型

数据库模型 `TestUICase` 中的时间字段类型已为datetime，无需修改：

| 字段 | 类型 | 说明 |
|------|------|------|
| created_time | DatetimeField | 由Tortoise ORM自动管理 |
| updated_time | DatetimeField | 由Tortoise ORM自动管理 |

### 序列化行为

修改后的序列化行为：

```
输入（Python）：datetime.datetime(2025, 1, 13, 10, 30, 0)
输出（JSON）："2025-01-13T10:30:00"
```

Pydantic会自动将datetime对象序列化为ISO 8601格式字符串，符合RESTful API标准。

### 前端兼容性验证

需要验证前端对时间格式的处理：

1. 确认前端使用的时间格式化库（如dayjs、moment等）能正确解析ISO 8601格式
2. 检查现有时间显示逻辑是否受影响
3. 如有特殊格式需求，在前端进行二次格式化

## 测试验证

### 测试用例设计

**测试1：创建测试用例**

目标：验证创建测试用例时时间字段正确序列化

步骤：
1. 调用创建测试用例API
2. 检查响应中的 `created_time` 和 `updated_time` 字段
3. 验证字段为ISO 8601格式字符串
4. 验证无Pydantic验证错误

预期结果：
- 响应状态码200
- created_time格式：`YYYY-MM-DDTHH:mm:ss` 或 `YYYY-MM-DDTHH:mm:ss.ffffff`
- updated_time格式：`YYYY-MM-DDTHH:mm:ss` 或 `YYYY-MM-DDTHH:mm:ss.ffffff`
- 无异常或错误消息

**测试2：获取测试用例列表**

目标：验证列表查询时批量数据的时间序列化

步骤：
1. 调用测试用例列表API
2. 检查返回列表中每个用例的时间字段
3. 验证时间格式一致性

预期结果：
- 所有用例的时间字段均为字符串格式
- 时间格式符合ISO 8601标准

**测试3：更新测试用例**

目标：验证更新操作后updated_time正确序列化

步骤：
1. 调用更新测试用例API
2. 检查响应中的 `updated_time` 是否更新
3. 验证新的时间戳格式正确

预期结果：
- updated_time值大于created_time
- 时间格式正确

**测试4：前端时间显示**

目标：验证前端能正确解析和显示时间

步骤：
1. 在前端页面查看测试用例列表
2. 检查创建时间和更新时间显示
3. 验证时间格式化符合UI需求

预期结果：
- 时间正确显示，无乱码或错误
- 格式符合用户阅读习惯（如："2025-01-13 10:30:00"）

### 回归测试

验证修改不影响其他使用 `BaseResponseSchema` 的Schema：

- `TestUserResponseSchema`：测试用户相关API
- `UIElementResponseSchema`：页面元素相关API
- `TestSuiteResponseSchema`：测试套件相关API
- `TestTaskResponseSchema`：测试单相关API
- `TestReportResponseSchema`：测试报告相关API

确保所有继承 `BaseResponseSchema` 的Schema均能正确处理时间字段。

## 风险评估

### 技术风险

| 风险项 | 风险等级 | 影响 | 缓解措施 |
|--------|---------|------|---------|
| 前端时间解析失败 | 低 | 时间显示异常 | 前端已使用标准时间库，ISO 8601为通用格式 |
| 时区处理问题 | 中 | 时间显示偏差 | 数据库使用UTC时间，前端根据用户时区转换 |
| 其他Schema受影响 | 低 | 其他功能异常 | 通过回归测试覆盖所有Schema |

### 兼容性风险

- Pydantic 2.x版本默认支持datetime序列化
- FastAPI框架自动处理JSON响应编码
- 前端JavaScript原生支持ISO 8601格式解析

风险等级：**低**

## 实施计划

### 实施步骤

1. 修改Schema定义
   - 修改 `BaseResponseSchema` 的时间字段类型
   - 修改 `TestCaseResponseSchema.last_execution_time` 字段类型

2. 代码验证
   - 检查所有构造响应Schema的代码
   - 确认无需额外转换逻辑

3. 单元测试
   - 测试创建测试用例API
   - 测试查询测试用例API
   - 测试更新测试用例API

4. 集成测试
   - 前后端联调验证
   - 检查时间显示效果

5. 回归测试
   - 验证其他使用BaseResponseSchema的功能

### 验收标准

- 所有测试用例API调用无Pydantic验证错误
- 时间字段格式为ISO 8601标准字符串
- 前端时间显示正常
- 其他继承BaseResponseSchema的Schema无异常
