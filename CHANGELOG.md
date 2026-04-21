# Changelog / 更新日志

> [返回 README](README.md) | [Back to README](README_en.md)

---

## v1.2.0 (2026-04-21) ⚠️ 重大升级

> **🔴 核心重构**：本次更新包含程序架构重构、UI 完全重写、新增多个 API 模块。

### 🚀 新增功能

#### 前端完全重构（独立 templates + static）

- **`templates/dashboard.html`** - 全新 Dashboard 页面，支持节点管理、版本历史、配置对比、Groups/Credentials/Models/Config 管理标签页
- **`templates/login.html`** - 独立登录页面
- **`templates/force_change_password.html`** - 强制修改密码页面
- **`static/css/dashboard.css`** - Dashboard 样式（681行）
- **`static/css/login.css`** - 登录页样式（138行）
- **`static/css/force_change_password.css`** - 强制修改密码样式（127行）
- **`static/js/dashboard.js`** (1747行) - Dashboard JavaScript 逻辑，包含版本历史时间轴、配置对比、ISO→Epoch 转换
- **`static/js/i18n.js`** (557行) - 国际化支持（中英文切换）

#### 新增 API 模块

- **`routes/pages.py`** (65行) - 独立页面路由蓝图
- **`routes/groups_api.py`** (78行) - 设备分组管理 REST API
- **`routes/credentials_api.py`** (127行) - 设备凭证管理 REST API
- **`routes/models_api.py`** (55行) - 设备型号管理 REST API
- **`routes/config_api.py`** (331行) - Oxidized 配置管理 REST API
- **`services/config_service.py`** (204行) - Oxidized 配置业务逻辑服务层
- **`models/group.py`** (61行) - 设备分组数据模型

### 🐛 错误修复

- **Oxidized OID 缓存 stale 问题修复** - 当 Oxidized 的 `@gitcache` 持有过期的 OID → node 映射时，版本历史 API 现在支持通过 `epoch` 参数直接读取 git 仓库历史，不再依赖 Oxidized 的内存缓存。解决了设备 IP 变更后版本历史无法加载的问题。

- **版本历史时间解析修复** - 前端 Dashboard 的 `viewVersionHistory()` 函数现在先将 `v.time` 的 ISO 时间字符串转换为 Unix epoch（`Math.floor(new Date(v.time).getTime() / 1000)`）再调用 API，解决了时间参数传递错误导致的版本历史加载失败问题。

- **登出重定向修复** - 修复 `auth.py` 中 `logout()` 函数重定向到硬编码 `/login` 路径而非 Flask Blueprint `pages.login` 的问题，现在正确使用 `redirect(url_for('pages.login'))`。

### 🔧 改进

- **移除华为 SSH Input 脚本** - 删除了 `oxidized-config/input/huaweissh.rb`，改用 `oxidized-config/model/huawei.rb` 统一处理，简化架构
- **Nginx 配置增强** - `nginx-proxy.conf` 新增 gzip 压缩（gzip_types: text/plain text/css application/json application/javascript text/xml application/xml）
- **数据库模块化** - `database.py` 中 `ensure_csv_synced()` 保留，新增 `init_database()` 数据库初始化
- **Routes 蓝图注册** - `routes/__init__.py` 中注册所有新增蓝图（pages, groups_api, credentials_api, models_api, config_api）
- **Huawei Model 增强** - `oxidized-config/model/huawei.rb` 增强，移除 input 依赖，统一使用 model

### 📝 文档

- 所有 README 文件添加完整更新日志
- README.md 添加架构图、故障排除章节
- 添加版本历史 OID cache stale 问题说明

---

## v1.0.0 (2026-01-10)

- 初始版本发布
- 节点管理与状态监控
- 配置版本对比
- 凭证管理
- 自研华为设备型号支持
