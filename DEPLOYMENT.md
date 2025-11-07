# Playwright 执行引擎部署指南

## 一、部署前准备

### 1.1 环境要求

- Python 3.13+
- MySQL 8.0+
- 至少 4GB 可用内存
- 至少 2GB 磁盘空间（用于存储执行日志和截图）

### 1.2 依赖安装

```bash
# 进入后端目录
cd backend

# 安装 Playwright
pip install playwright

# 安装浏览器
playwright install chromium

# （可选）安装其他浏览器
playwright install firefox
playwright install webkit
```

## 二、文件部署

### 2.1 复制核心文件到实际项目

将以下文件复制到实际项目的对应位置：

```bash
# 从工作空间复制到实际项目
SOURCE_DIR="/Users/gavenhwang/.qoder/worktree/test-galaxy/qoder/implement-playwright-executor-1762395629"
TARGET_DIR="/Users/gavenhwang/Documents/Code/PycharmProjects/test-galaxy"

# 复制核心模块
cp $SOURCE_DIR/backend/app/core/config_generator.py $TARGET_DIR/backend/app/core/
cp $SOURCE_DIR/backend/app/core/selector_builder.py $TARGET_DIR/backend/app/core/
cp $SOURCE_DIR/backend/app/core/script_generator.py $TARGET_DIR/backend/app/core/
cp $SOURCE_DIR/backend/app/core/case_executor.py $TARGET_DIR/backend/app/core/
cp $SOURCE_DIR/backend/app/core/result_collector.py $TARGET_DIR/backend/app/core/
cp $SOURCE_DIR/backend/app/core/task_execution_scheduler.py $TARGET_DIR/backend/app/core/

# 复制更新的 API 文件
cp $SOURCE_DIR/backend/app/api/ui_test_task.py $TARGET_DIR/backend/app/api/

# 复制文档
cp $SOURCE_DIR/IMPLEMENTATION_GUIDE.md $TARGET_DIR/
```

### 2.2 创建执行目录

```bash
cd /Users/gavenhwang/Documents/Code/PycharmProjects/test-galaxy
mkdir -p test_executions
chmod 755 test_executions
```

## 三、配置调整

### 3.1 环境变量配置

在 `backend/app/core/config_generator.py` 中，根据实际环境调整环境变量映射：

```python
def _get_environment_variables(self, environment: str) -> Dict:
    """获取环境变量配置"""
    env_map = {
        '测试环境': {
            'host': 'http://localhost:5173',  # 修改为实际测试环境地址
            'api_host': 'http://localhost:9998'
        },
        '生产环境': {
            'host': 'http://www.example.com',  # 修改为实际生产环境地址
            'api_host': 'http://api.example.com'
        }
    }
    # ... 其余代码
```

### 3.2 默认配置调整

根据需要调整默认执行配置：

```python
# 在 config_generator.py 中修改默认值
if 'max_workers' not in config['execute_config']:
    config['execute_config']['max_workers'] = 4  # 根据服务器性能调整
```

## 四、测试验证

### 4.1 基础功能测试

```bash
# 启动后端服务
cd backend
python run.py

# 测试 API（使用 Postman 或 curl）
# 1. 创建测试单
# 2. 执行测试单
# 3. 查看执行进度
# 4. 查看执行结果
```

### 4.2 脚本生成测试

手动触发一次执行，检查生成的文件：

```bash
# 查看工作目录
ls -la test_executions/task_*

# 查看配置文件
cat test_executions/task_*/config.json

# 查看生成的脚本
ls -la test_executions/task_*/scripts/

# 手动执行脚本测试
cd test_executions/task_*
DEBUG=1 HEADLESS=0 python scripts/case_001_001.py
```

### 4.3 并发执行测试

测试不同并发配置：

```json
// 测试 1：串行执行
{
  "execute_config": {
    "parallel_mode": "serial"
  }
}

// 测试 2：小并发
{
  "execute_config": {
    "parallel_mode": "process",
    "max_workers": 2
  }
}

// 测试 3：自动并发
{
  "execute_config": {
    "parallel_mode": "process",
    "max_workers": "auto"
  }
}
```

## 五、监控和维护

### 5.1 日志监控

```bash
# 查看系统日志
tail -f backend/app/logs/app.log

# 查看执行日志
tail -f test_executions/task_*/logs/case_*.json
```

### 5.2 性能监控

监控以下指标：

- CPU 使用率
- 内存使用率
- 磁盘空间
- 数据库连接数
- 执行成功率

### 5.3 定期维护

```bash
# 清理旧的执行目录（保留 30 天）
find test_executions -type d -name "task_*" -mtime +30 -exec rm -rf {} \;

# 压缩历史日志
find test_executions -type f -name "*.json" -mtime +7 -exec gzip {} \;

# 清理失败截图（保留 7 天）
find test_executions/*/screenshots -type f -mtime +7 -delete
```

## 六、故障恢复

### 6.1 常见故障

**故障1：执行卡住**
```bash
# 查找僵尸进程
ps aux | grep python | grep case_

# 杀死僵尸进程
kill -9 <pid>

# 重置测试单状态
# 在数据库中手动更新 test_ui_tasks 表的 status 字段
```

**故障2：磁盘空间不足**
```bash
# 清理执行目录
rm -rf test_executions/task_*

# 清理日志
find backend/app/logs -type f -mtime +30 -delete
```

**故障3：浏览器崩溃**
```bash
# 重新安装浏览器
playwright install --force chromium

# 检查浏览器进程
ps aux | grep chromium

# 清理浏览器缓存
rm -rf ~/.cache/ms-playwright/
```

### 6.2 数据备份

定期备份重要数据：

```bash
# 备份执行日志
tar -czf logs_backup_$(date +%Y%m%d).tar.gz test_executions/

# 备份数据库
mysqldump -u root -p test-galaxy > backup_$(date +%Y%m%d).sql
```

## 七、性能优化

### 7.1 系统级优化

```bash
# 增加文件描述符限制
ulimit -n 65536

# 增加进程数限制
ulimit -u 4096
```

### 7.2 应用级优化

1. **并发数调优**
   - 根据 CPU 核心数设置 max_workers
   - 监控系统资源使用情况
   - 动态调整并发数

2. **超时时间优化**
   - 根据实际网络情况调整 timeout
   - 为慢速操作增加 wait_time

3. **资源清理优化**
   - 及时清理执行目录
   - 压缩历史日志
   - 限制截图大小和数量

## 八、安全加固

### 8.1 文件权限

```bash
# 设置执行目录权限
chmod 750 test_executions
chown -R app_user:app_group test_executions

# 设置脚本权限
chmod 700 test_executions/*/scripts/*.py

# 设置配置文件权限
chmod 600 test_executions/*/config.json
```

### 8.2 密码加密

建议在生产环境中：

1. 使用环境变量存储敏感信息
2. 使用密钥管理服务（如 Vault）
3. 加密配置文件
4. 定期轮换密码

### 8.3 访问控制

1. 限制执行目录访问权限
2. 使用 RBAC 控制 API 访问
3. 记录操作审计日志

## 九、升级和回滚

### 9.1 升级流程

1. 备份当前版本
2. 停止服务
3. 部署新版本
4. 运行测试
5. 启动服务
6. 验证功能

### 9.2 回滚流程

1. 停止服务
2. 恢复备份版本
3. 恢复数据库（如需要）
4. 启动服务
5. 验证功能

## 十、技术支持

### 10.1 日志收集

遇到问题时，收集以下信息：

1. 系统日志：`backend/app/logs/app.log`
2. 执行日志：`test_executions/task_*/logs/`
3. 错误截图：`test_executions/task_*/screenshots/`
4. 数据库记录：执行记录表
5. 系统信息：CPU、内存、磁盘

### 10.2 问题报告

报告问题时，请提供：

1. 问题描述
2. 复现步骤
3. 预期结果
4. 实际结果
5. 日志信息
6. 环境信息

## 附录：快速部署脚本

```bash
#!/bin/bash

# 部署脚本
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TARGET_DIR="/Users/gavenhwang/Documents/Code/PycharmProjects/test-galaxy"

echo "开始部署 Playwright 执行引擎..."

# 1. 安装依赖
echo "安装依赖..."
cd $TARGET_DIR/backend
pip install playwright
playwright install chromium

# 2. 创建目录
echo "创建执行目录..."
mkdir -p $TARGET_DIR/test_executions
chmod 755 $TARGET_DIR/test_executions

# 3. 复制文件
echo "复制核心文件..."
cp $SCRIPT_DIR/backend/app/core/*.py $TARGET_DIR/backend/app/core/
cp $SCRIPT_DIR/backend/app/api/ui_test_task.py $TARGET_DIR/backend/app/api/

# 4. 验证
echo "验证安装..."
python -c "import playwright; print('Playwright 安装成功')"

echo "部署完成！"
echo "请查看 IMPLEMENTATION_GUIDE.md 了解使用方法"
```
