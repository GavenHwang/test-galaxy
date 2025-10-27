# Galaxy Platform

基于 Vue 3 + FastAPI 的全栈平台项目

## 📋 项目概述

- **前端：** Vue 3 + Vite + Element Plus + Pinia
- **后端：** FastAPI + Tortoise ORM + MySQL
- **部署：** Uvicorn (开发) + 生产环境支持

## 🚀 快速开始

### 环境要求

- **Node.js:** >= 16.0.0
- **Python:** >= 3.13
- **MySQL:** >= 8.0
- **pnpm:** >= 10.13.1 (必须使用，项目统一包管理器)

### 🗂️ 项目结构

```
test-galaxy/
├── backend/                 # 后端 FastAPI 应用
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心功能
│   │   ├── models/         # 数据模型
│   │   └── config/         # 配置文件
│   ├── requirements.txt    # Python 依赖
│   └── run.py             # 后端启动文件
├── frontend/               # 前端 Vue 应用
│   ├── src/               # 源代码
│   ├── public/            # 静态资源
│   ├── package.json       # 前端依赖
│   └── vite.config.js     # Vite 配置
└── README.md              # 项目说明文档
```

## 📦 安装与运行

### 后端安装与启动

1. **进入后端目录**
   ```bash
   cd backend
   ```

2. **创建并激活虚拟环境**
   ```bash
   # 使用你习惯的虚拟环境管理工具
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安装 Python 依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置数据库连接**

   确保数据库配置正确（检查 `app/settings/config.py` 中的数据库配置）

5. **启动后端服务**
   ```bash
   python run.py
   ```

   **后端服务地址：** http://localhost:9998

### 前端安装与启动

1. **进入前端目录**
   ```bash
   cd frontend
   ```

2. **安装 pnpm（如果未安装）**
   ```bash
   # 全局安装 pnpm
   npm install -g pnpm

   # 或者使用其他安装方式
   # curl -fsSL https://get.pnpm.io/install.sh | sh
   ```

3. **安装前端依赖**
   ```bash
   # 必须使用 pnpm
   pnpm install
   ```

4. **启动前端开发服务器**
   ```bash
   # 必须使用 pnpm
   pnpm dev
   ```

   **前端服务地址：** http://localhost:5173

## 🔑 默认登录凭据

系统启动时会自动创建超级管理员账号：

- **用户名：** `admin`
- **密码：** `111111aA`

**⚠️ 重要提示：**
- 密码要求包含大小写字母和数字，至少8位
- 首次登录后请立即修改默认密码
- admin 用户不能被删除或重置密码

## ⚙️ 配置说明

### 后端配置

- **数据库配置：** 修改 `app/settings/config.py` 中的数据库连接信息
- **服务端口：** 在 `run.py` 中修改（默认 9998）
- **其他配置：** 查看配置文件了解详细选项

### 前端配置

- **API 地址：** 在前端代码中配置后端 API 地址
- **开发端口：** 在 `vite.config.js` 中修改（默认 5173）

## 🔧 开发工具

### 推荐的 IDE 和插件

- **后端开发：** PyCharm / VS Code + Python 插件
- **前端开发：** VS Code + Vue 3 插件 (Volar)
- **数据库管理：** MySQL Workbench / phpMyAdmin

### 代码格式化工具

- **Python：** Black, isort
- **JavaScript/TypeScript：** ESLint, Prettier

## 🐛 常见问题与解决方案

### 1. Python 依赖安装失败

**问题：** `ModuleNotFoundError: No module named 'tortoise'`

**解决方案：**
```bash
# 确保 requirements.txt 文件编码正确
# 如果遇到编码问题，删除 requirements.txt 并重新创建
pip install -r requirements.txt
```

### 2. 前端依赖权限问题

**问题：** `Permission denied` 运行 vite

**解决方案：**
```bash
# 项目统一使用 pnpm，避免权限问题
pnpm install
pnpm dev

# 如果仍有权限问题，修复可执行权限
chmod +x node_modules/.bin/*
```

### 3. 团队成员未安装 pnpm

**问题：** 团队成员习惯使用 npm 或 yarn

**解决方案：**
```bash
# 安装 pnpm（选择其中一种方式）
# 方式1：通过 npm 安装
npm install -g pnpm

# 方式2：通过官方脚本安装
curl -fsSL https://get.pnpm.io/install.sh | sh

# 方式3：通过 Homebrew（macOS）
brew install pnpm
```

**注意：** 本项目统一使用 pnpm 作为包管理器，以确保依赖一致性和更好的性能。

### 4. 数据库连接失败

**问题：** `Can't connect to MySQL server`

**解决方案：**
- 确保 MySQL 服务正在运行
- 检查数据库连接配置
- 确认数据库用户权限

### 5. 端口冲突

**问题：** `Address already in use`

**解决方案：**
- 修改端口配置
- 或停止占用端口的服务
  ```bash
  # 查找占用端口的进程
  lsof -i :9998  # 后端端口
  lsof -i :5173  # 前端端口
  ```

### 6. Virtual Environment 问题

**建议：** 始终在虚拟环境中运行 Python 代码

```bash
# 创建虚拟环境
python -m venv /path/to/your/venv

# 激活虚拟环境
source /path/to/your/venv/bin/activate  # Linux/Mac
# 或
/path/to/your/venv/Scripts/activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

## 📝 开发注意事项

### 后端开发

1. **数据库迁移：** 使用 Aerich 进行数据库迁移管理
2. **API 文档：** 访问 `http://localhost:9998/docs` 查看自动生成的 API 文档
3. **代码规范：** 遵循 FastAPI 最佳实践

### 前端开发

1. **组件开发：** 使用 Vue 3 Composition API
2. **状态管理：** 使用 Pinia 进行状态管理
3. **路由管理：** 使用 Vue Router 4
4. **UI 组件：** 基于 Element Plus

## 🚀 部署指南

### 开发环境

- **前端：** `pnpm dev`（必须使用 pnpm）
- **后端：** `python run.py`

### 生产环境

1. **前端构建：**
   ```bash
   # 使用 pnpm 构建生产版本
   pnpm build
   ```

2. **后端部署：**
   ```bash
   # 使用生产级 ASGI 服务器
   uvicorn app:app --host 0.0.0.0 --port 9998 --workers 4
   ```

## 📞 技术支持

如果遇到问题，请检查：

1. **环境配置：** 确保所有依赖都正确安装
2. **网络连接：** 确保可以访问 npm/pypi 源
3. **数据库服务：** 确保 MySQL 服务正常运行
4. **端口占用：** 确保端口没有被其他程序占用

## 🔄 更新日志

- **v1.0.0:** 初始版本，包含基本的前后端架构
- 修复了 requirements.txt 编码问题
- 添加了完整的安装和运行文档

---

**🎉 现在你已经准备好开始开发了！**

使用默认账号登录系统：`admin` / `111111aA`