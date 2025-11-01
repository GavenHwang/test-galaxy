# 颜色配置指南

## 📁 配置文件位置

所有颜色配置统一在：`src/assets/less/variables.less`

## 🎨 如何修改主题颜色

### 修改主色调（红色系）

如果要将整个系统的主色调从红色改为其他颜色（例如蓝色），只需修改以下变量：

```less
// 在 src/assets/less/variables.less 中修改

// 主色调（红色系 → 改为蓝色系）
@primary-color: #1890ff;              // 主色（从 #d9232c 改为蓝色）
@primary-hover: #40a9ff;              // 悬停色（从 #e04f56 改为浅蓝）
@primary-active: #096dd9;             // 激活/按下色（从 #ae1c23 改为深蓝）
@primary-light: #91d5ff;              // 浅色（禁用状态）
@primary-lighter: #e6f7ff;            // 更浅色（plain 按钮背景）
@primary-border: #91d5ff;             // 边框色（plain 按钮）
@primary-shadow: rgba(24, 144, 255, 0.1);  // 阴影/半透明背景
```

**保存后，所有使用主色的地方会自动更新：**
- 所有按钮（primary、danger 类型）
- 链接
- 选中状态（checkbox、radio、switch）
- 分页激活状态
- 输入框聚焦边框
- 菜单激活项
- 标签页激活项
- 等等...

### 修改辅助色

```less
// 成功色（绿色）
@success-color: #67c23a;
@success-hover: #85ce61;

// 警告色（橙色）
@warning-color: #e6a23c;
@warning-hover: #ebb563;

// 信息色（灰色）
@info-color: #909399;
@info-hover: #a6a9ad;
```

### 修改文本颜色

```less
@text-primary: #333333;               // 主要文本
@text-secondary: #666666;             // 次要文本
@text-placeholder: #909399;           // 占位符文本
@text-disabled: #c0c4cc;              // 禁用文本
@text-white: #ffffff;                 // 白色文本
```

### 修改背景颜色

```less
@bg-white: #ffffff;                   // 白色背景
@bg-page: #f0f2f5;                    // 页面背景
@bg-light: #fafafa;                   // 浅背景（表头等）
@bg-hover: #f5f7fa;                   // 悬停背景
```

### 修改边框颜色

```less
@border-base: #dcdfe6;                // 基础边框
@border-light: #e4e7ed;               // 浅边框
@border-lighter: #ebeef5;             // 更浅边框
@border-dark: #d3d4d6;                // 深边框
```

### 修改圆角

```less
@border-radius-base: 4px;             // 基础圆角
@border-radius-medium: 6px;           // 中等圆角
@border-radius-large: 8px;            // 大圆角
@border-radius-xlarge: 12px;          // 超大圆角
@border-radius-round: 50%;            // 圆形
```

### 修改间距

```less
@spacing-xs: 4px;                     // 超小间距
@spacing-sm: 8px;                     // 小间距
@spacing-md: 12px;                    // 中等间距
@spacing-lg: 16px;                    // 大间距
@spacing-xl: 20px;                    // 超大间距
@spacing-xxl: 24px;                   // 特大间距
```

### 修改字体大小

```less
@font-size-xs: 12px;                  // 超小字体
@font-size-sm: 13px;                  // 小字体
@font-size-base: 14px;                // 基础字体
@font-size-md: 16px;                  // 中等字体
@font-size-lg: 18px;                  // 大字体
@font-size-xl: 20px;                  // 超大字体
@font-size-xxl: 24px;                 // 特大字体
```

## 📝 在组件中使用变量

在任何 `.vue` 文件的 `<style>` 标签中使用：

```vue
<style scoped lang="less">
@import '@/assets/less/variables.less';

.my-component {
  color: @primary-color;              // 使用主色
  background: @bg-white;              // 使用白色背景
  padding: @spacing-lg;               // 使用大间距
  border-radius: @border-radius-medium;  // 使用中等圆角
  transition: @transition-base;       // 使用基础过渡
  
  &:hover {
    color: @primary-hover;            // 悬停时使用悬停色
    background: @bg-hover;            // 悬停背景
  }
}
</style>
```

## ⚠️ 注意事项

1. **必须在 `<style>` 标签中添加 `lang="less"`**
   ```vue
   <style scoped lang="less">  <!-- 必须有 lang="less" -->
   @import '@/assets/less/variables.less';
   </style>
   ```

2. **每次修改 `variables.less` 后需要重启开发服务器**
   ```bash
   # 停止当前服务 (Ctrl+C)
   # 重新启动
   cd frontend && pnpm dev
   ```

3. **避免在组件中硬编码颜色**
   
   ❌ 不好的做法：
   ```css
   .button { color: #d9232c; }
   ```
   
   ✅ 好的做法：
   ```less
   @import '@/assets/less/variables.less';
   .button { color: @primary-color; }
   ```

## 🎯 常见场景示例

### 场景1: 修改整站主题为蓝色

只需修改 `variables.less` 中的主色：
```less
@primary-color: #1890ff;
@primary-hover: #40a9ff;
@primary-active: #096dd9;
```

### 场景2: 增加圆角

修改圆角变量：
```less
@border-radius-base: 8px;      // 从 4px 增大到 8px
@border-radius-medium: 12px;   // 从 6px 增大到 12px
@border-radius-large: 16px;    // 从 8px 增大到 16px
```

### 场景3: 调整间距

修改间距变量：
```less
@spacing-lg: 20px;    // 从 16px 增大到 20px
@spacing-xl: 28px;    // 从 20px 增大到 28px
```

## 📦 文件结构

```
frontend/src/assets/less/
├── variables.less    ← 所有颜色和样式变量（修改这里）
├── index.less        ← 全局样式（使用变量，一般不需要修改）
└── reset.less        ← 重置样式（一般不需要修改）
```

## 🔄 更新流程

1. 打开 `frontend/src/assets/less/variables.less`
2. 修改需要的颜色变量
3. 保存文件
4. 重启开发服务器（`pnpm dev`）
5. 刷新浏览器查看效果

---

**提示**: 只需修改 `variables.less` 一个文件，就能控制整个系统的颜色主题！
