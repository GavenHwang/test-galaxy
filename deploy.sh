#!/bin/bash

# Playwright 执行引擎快速部署脚本
# 用途：快速部署核心文件到实际项目

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
WORKSPACE_DIR="/Users/gavenhwang/.qoder/worktree/test-galaxy/qoder/implement-playwright-executor-1762395629"
PROJECT_DIR="/Users/gavenhwang/Documents/Code/PycharmProjects/test-galaxy"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Playwright 执行引擎部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查源目录
if [ ! -d "$WORKSPACE_DIR" ]; then
    echo -e "${RED}错误: 源目录不存在: $WORKSPACE_DIR${NC}"
    exit 1
fi

# 检查目标目录
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}错误: 目标项目目录不存在: $PROJECT_DIR${NC}"
    exit 1
fi

echo -e "${YELLOW}源目录: $WORKSPACE_DIR${NC}"
echo -e "${YELLOW}目标目录: $PROJECT_DIR${NC}"
echo ""

# 1. 安装依赖
echo -e "${GREEN}[1/6] 检查并安装依赖...${NC}"
cd "$PROJECT_DIR/backend"

if ! python -c "import playwright" 2>/dev/null; then
    echo "安装 Playwright..."
    pip install playwright
    echo "安装浏览器..."
    playwright install chromium
else
    echo "Playwright 已安装"
fi
echo ""

# 2. 创建执行目录
echo -e "${GREEN}[2/6] 创建执行目录...${NC}"
mkdir -p "$PROJECT_DIR/test_executions"
chmod 755 "$PROJECT_DIR/test_executions"
echo "执行目录创建成功: $PROJECT_DIR/test_executions"
echo ""

# 3. 复制核心模块
echo -e "${GREEN}[3/6] 复制核心模块文件...${NC}"
CORE_FILES=(
    "config_generator.py"
    "selector_builder.py"
    "script_generator.py"
    "case_executor.py"
    "result_collector.py"
    "task_execution_scheduler.py"
)

for file in "${CORE_FILES[@]}"; do
    src="$WORKSPACE_DIR/backend/app/core/$file"
    dst="$PROJECT_DIR/backend/app/core/$file"
    
    if [ -f "$src" ]; then
        cp "$src" "$dst"
        echo "  ✓ $file"
    else
        echo -e "${RED}  ✗ $file (源文件不存在)${NC}"
    fi
done
echo ""

# 4. 复制 API 文件
echo -e "${GREEN}[4/6] 复制 API 文件...${NC}"
src="$WORKSPACE_DIR/backend/app/api/ui_test_task.py"
dst="$PROJECT_DIR/backend/app/api/ui_test_task.py"

if [ -f "$src" ]; then
    # 备份原文件
    if [ -f "$dst" ]; then
        cp "$dst" "$dst.backup.$(date +%Y%m%d%H%M%S)"
        echo "  原文件已备份"
    fi
    
    cp "$src" "$dst"
    echo "  ✓ ui_test_task.py"
else
    echo -e "${RED}  ✗ ui_test_task.py (源文件不存在)${NC}"
fi
echo ""

# 5. 复制文档
echo -e "${GREEN}[5/6] 复制文档文件...${NC}"
DOC_FILES=(
    "README.md"
    "IMPLEMENTATION_GUIDE.md"
    "DEPLOYMENT.md"
)

for file in "${DOC_FILES[@]}"; do
    src="$WORKSPACE_DIR/$file"
    dst="$PROJECT_DIR/$file"
    
    if [ -f "$src" ]; then
        cp "$src" "$dst"
        echo "  ✓ $file"
    else
        echo -e "${YELLOW}  - $file (跳过)${NC}"
    fi
done
echo ""

# 6. 验证安装
echo -e "${GREEN}[6/6] 验证安装...${NC}"

# 检查 Playwright
if python -c "import playwright; print('Playwright 版本:', playwright.__version__)" 2>/dev/null; then
    echo "  ✓ Playwright 验证通过"
else
    echo -e "${RED}  ✗ Playwright 验证失败${NC}"
fi

# 检查核心文件
missing_files=0
for file in "${CORE_FILES[@]}"; do
    if [ ! -f "$PROJECT_DIR/backend/app/core/$file" ]; then
        echo -e "${RED}  ✗ 缺失文件: $file${NC}"
        missing_files=$((missing_files+1))
    fi
done

if [ $missing_files -eq 0 ]; then
    echo "  ✓ 所有核心文件已就位"
fi

echo ""

# 完成
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}下一步：${NC}"
echo "1. 启动后端服务："
echo "   cd $PROJECT_DIR/backend && python run.py"
echo ""
echo "2. 创建测试单并执行"
echo "   POST /api/test-tasks"
echo "   POST /api/test-tasks/{task_id}/execute"
echo ""
echo "3. 查看详细使用说明："
echo "   cat $PROJECT_DIR/IMPLEMENTATION_GUIDE.md"
echo ""
echo -e "${GREEN}祝你使用愉快！${NC}"
