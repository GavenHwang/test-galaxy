# Playwright 执行引擎实施指南

## 一、已完成的工作

### 1.1 核心模块

已创建以下核心模块：

1. **配置生成器** (`backend/app/core/config_generator.py`)
   - 生成测试执行配置文件 config.json
   - 收集测试用户凭证
   - 管理环境变量

2. **选择器构建器** (`backend/app/core/selector_builder.py`)
   - 转换数据库选择器为 Playwright 格式
   - 处理特殊字符转义

3. **脚本生成器** (`backend/app/core/script_generator.py`)
   - 为每个用例生成独立的 Python 脚本
   - 支持配置变量替换
   - 包含完整的日志记录和异常处理

4. **用例执行器** (`backend/app/core/case_executor.py`)
   - 使用 subprocess 执行独立脚本
   - 超时控制和进程管理

5. **结果收集器** (`backend/app/core/result_collector.py`)
   - 读取执行日志文件
   - 写入数据库执行记录

6. **执行调度器** (`backend/app/core/task_execution_scheduler.py`)
   - 协调整个测试单执行流程
   - 支持串行和并发执行
   - 进度追踪和状态更新

7. **API 接口更新** (`backend/app/api/ui_test_task.py`)
   - 完善 execute_test_task 接口
   - 后台异步执行支持

## 二、使用步骤

### 2.1 安装依赖

```bash
cd backend
pip install playwright
playwright install chromium
```

### 2.2 创建测试单并执行

1. **创建测试单**
```
POST /api/test-tasks
{
  "name": "回归测试-2024-01-15",
  "description": "全面回归测试",
  "environment": "测试环境",
  "execute_config": {
    "browser": "chromium",
    "headless": true,
    "timeout": 30000,
    "max_workers": 4,
    "parallel_mode": "process"
  },
  "suites": [1, 2],
  "cases": [3, 4, 5]
}
```

2. **执行测试单**
```
POST /api/test-tasks/{task_id}/execute
```

3. **查看执行进度**
```
GET /api/test-tasks/{task_id}/progress
```

4. **查看执行结果**
```
GET /api/test-tasks/{task_id}/reports
```

### 2.3 手动执行脚本

生成的脚本可以独立执行：

```bash
cd test_executions/task_123_20240115143000

# 正常执行
python scripts/case_001_001.py

# 调试模式（有头浏览器，详细日志）
DEBUG=1 HEADLESS=0 python scripts/case_001_001.py

# 慢速执行（便于观察）
DEBUG=1 HEADLESS=0 SLOW_MO=500 python scripts/case_001_001.py
```

## 三、工作目录结构

执行后会生成以下目录结构：

```
test_executions/
└── task_123_20240115143000/
    ├── config.json              # 配置文件
    ├── scripts/                 # 脚本目录
    │   ├── case_001_001.py
    │   ├── case_002_002.py
    │   └── ...
    ├── logs/                    # 日志目录
    │   ├── case_001_001.json
    │   ├── case_002_002.json
    │   └── ...
    └── screenshots/             # 截图目录
        ├── case_001_step_003_20240115143500.png
        └── ...
```

## 四、配置说明

### 4.1 执行配置（execute_config）

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| browser | string | chromium | 浏览器类型：chromium/firefox/webkit |
| headless | boolean | true | 是否无头模式 |
| timeout | int | 30000 | 超时时间（毫秒） |
| continue_on_failure | boolean | true | 失败后是否继续 |
| retry_count | int | 2 | 失败重试次数 |
| auto_screenshot | boolean | true | 失败时自动截图 |
| viewport | object | {width:1920, height:1080} | 视口大小 |
| max_workers | int/string | 4 | 并发数，'auto' 自动检测 |
| parallel_mode | string | process | 并发模式：process/serial |
| worker_timeout | int | 300 | Worker 超时时间（秒） |

### 4.2 环境变量

配置文件中的环境变量可以根据不同环境定制：

```json
{
  "environment_variables": {
    "host": "http://localhost:5173",
    "api_host": "http://localhost:9998",
    "admin_username": "admin",
    "admin_password": "111111aA"
  }
}
```

## 五、日志格式

### 5.1 执行日志 (case_xxx.json)

```json
{
  "case_info": {
    "case_id": 1,
    "case_name": "用户登录功能测试",
    "priority": "高",
    "module": "用户模块"
  },
  "execution_info": {
    "start_time": "2024-01-15 14:30:05",
    "end_time": "2024-01-15 14:30:35",
    "duration": 30,
    "status": "通过",
    "error_message": null
  },
  "steps": [
    {
      "step_number": 1,
      "action": "navigate",
      "description": "打开登录页面",
      "start_time": "2024-01-15 14:30:05",
      "end_time": "2024-01-15 14:30:07",
      "duration": 2000,
      "status": "通过",
      "error_message": null,
      "screenshot_path": null
    }
  ],
  "retry_count": 0,
  "screenshots": []
}
```

## 六、故障排查

### 6.1 常见问题

**问题1：浏览器启动失败**
```
解决方案：
1. 确认已安装 playwright: pip install playwright
2. 安装浏览器: playwright install chromium
3. 检查系统权限
```

**问题2：找不到元素**
```
解决方案：
1. 检查元素选择器是否正确
2. 增加等待时间
3. 使用 wait_for_element 步骤
4. 启用调试模式查看页面状态
```

**问题3：执行超时**
```
解决方案：
1. 增加 timeout 配置
2. 检查网络连接
3. 优化测试步骤
```

**问题4：并发执行失败**
```
解决方案：
1. 降低 max_workers 数量
2. 切换到串行模式 parallel_mode='serial'
3. 检查系统资源（内存、CPU）
```

### 6.2 调试技巧

1. **启用调试模式**
```bash
DEBUG=1 HEADLESS=0 python scripts/case_001_001.py
```

2. **查看执行日志**
```bash
cat logs/case_001_001.json | python -m json.tool
```

3. **查看截图**
```bash
open screenshots/case_001_step_003_*.png
```

## 七、性能优化建议

### 7.1 并发配置

- **小型测试**（< 10 个用例）：串行执行或 max_workers=2
- **中型测试**（10-50 个用例）：max_workers=4
- **大型测试**（> 50 个用例）：max_workers='auto'

### 7.2 资源管理

- 定期清理执行目录（保留最近 30 天）
- 截图使用 JPEG 格式（减小文件大小）
- 日志文件压缩存储

## 八、后续扩展

### 8.1 已规划功能

- [ ] WebSocket 实时进度推送
- [ ] 执行报告 HTML 导出
- [ ] 邮件通知
- [ ] 分布式执行支持
- [ ] 性能指标采集
- [ ] 智能失败分析

### 8.2 扩展点

执行引擎设计为模块化，可以方便地扩展：

1. **自定义操作类型**：在 ScriptGenerator 中添加新的 action 映射
2. **自定义浏览器配置**：修改 ConfigGenerator 的默认配置
3. **自定义日志格式**：修改脚本模板中的日志记录逻辑
4. **自定义结果处理**：扩展 ResultCollector 的处理逻辑

## 九、注意事项

### 9.1 安全性

- 配置文件中的密码已做基础混淆（实际项目应加密）
- 脚本文件权限设置为 700（仅所有者可执行）
- 执行日志中的敏感信息需要脱敏处理

### 9.2 兼容性

- Python 版本：>= 3.13
- Playwright 版本：>= 1.40
- 操作系统：支持 macOS、Linux、Windows

### 9.3 限制

- 单次执行建议不超过 1000 个用例
- 并发数建议不超过 CPU 核心数的 2 倍
- 脚本文件保留期限：7 天（可配置）
- 日志文件保留期限：30 天

## 十、测试验证

### 10.1 单元测试

创建简单的测试用例验证功能：

1. 创建测试用户
2. 创建页面元素
3. 创建测试用例（包含简单步骤）
4. 创建测试单
5. 执行测试单
6. 查看执行结果

### 10.2 集成测试

完整流程测试：

1. 创建完整的测试场景（登录、操作、断言）
2. 执行串行模式
3. 执行并发模式
4. 验证失败场景处理
5. 验证手动执行脚本
6. 验证结果报告生成

## 十一、联系与支持

如遇到问题，请查看：

1. 执行日志文件
2. 数据库执行记录
3. 系统日志
4. 截图文件

详细的设计文档：`.qoder/quests/implement-playwright-executor.md`
