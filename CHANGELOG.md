# Changelog / 更新日志

> [返回 README](README.md) | [Back to README](README_en.md)

---

## v1.2.0 (2026-04-21) ⚠️ 重大升级 / ⚠️ MAJOR UPGRADE

> **🔴 核心重构**：本次更新包含程序架构重构、UI 完全重写、新增多个 API 模块。
> **🔴 Core Refactoring**: This release includes application architecture refactoring, complete UI rewrite, and new API modules.

### 🚀 新增功能 / New Features

#### 前端完全重构（独立 templates + static）/ Complete Frontend Refactoring (Independent templates + static)

| 中文 | English |
|------|---------|
| **`templates/dashboard.html`** - 全新 Dashboard 页面，支持节点管理、版本历史、配置对比、Groups/Credentials/Models/Config 管理标签页 | **`templates/dashboard.html`** - New Dashboard page with node management, version history, config comparison, Groups/Credentials/Models/Config management tabs |
| **`templates/login.html`** - 独立登录页面 | **`templates/login.html`** - Standalone login page |
| **`templates/force_change_password.html`** - 强制修改密码页面 | **`templates/force_change_password.html`** - Force change password page |
| **`static/css/dashboard.css`** - Dashboard 样式（681行） | **`static/css/dashboard.css`** - Dashboard styles (681 lines) |
| **`static/css/login.css`** - 登录页样式（138行） | **`static/css/login.css`** - Login page styles (138 lines) |
| **`static/css/force_change_password.css`** - 强制修改密码样式（127行） | **`static/css/force_change_password.css`** - Force change password styles (127 lines) |
| **`static/js/dashboard.js`** (1747行) - Dashboard JavaScript 逻辑，包含版本历史时间轴、配置对比、ISO→Epoch 转换 | **`static/js/dashboard.js`** (1747 lines) - Dashboard JavaScript logic, including version history timeline, config comparison, ISO→Epoch conversion |
| **`static/js/i18n.js`** (557行) - 国际化支持（中英文切换） | **`static/js/i18n.js`** (557 lines) - Internationalization support (EN/ZH toggle) |

#### 新增 API 模块 / New API Modules

| 中文 | English |
|------|---------|
| **`routes/pages.py`** (65行) - 独立页面路由蓝图 | **`routes/pages.py`** (65 lines) - Standalone page routing blueprint |
| **`routes/groups_api.py`** (78行) - 设备分组管理 REST API | **`routes/groups_api.py`** (78 lines) - Device group management REST API |
| **`routes/credentials_api.py`** (127行) - 设备凭证管理 REST API | **`routes/credentials_api.py`** (127 lines) - Device credential management REST API |
| **`routes/models_api.py`** (55行) - 设备型号管理 REST API | **`routes/models_api.py`** (55 lines) - Device model management REST API |
| **`routes/config_api.py`** (331行) - Oxidized 配置管理 REST API | **`routes/config_api.py`** (331 lines) - Oxidized configuration management REST API |
| **`services/config_service.py`** (204行) - Oxidized 配置业务逻辑服务层 | **`services/config_service.py`** (204 lines) - Oxidized configuration business logic service layer |
| **`models/group.py`** (61行) - 设备分组数据模型 | **`models/group.py`** (61 lines) - Device group data model |

### 🐛 错误修复 / Bug Fixes

| 中文 | English |
|------|---------|
| **Oxidized OID 缓存 stale 问题修复** - 当 Oxidized 的 `@gitcache` 持有过期的 OID → node 映射时，版本历史 API 现在支持通过 `epoch` 参数直接读取 git 仓库历史，不再依赖 Oxidized 的内存缓存。解决了设备 IP 变更后版本历史无法加载的问题。 | **Oxidized OID Cache Stale Fix** - When Oxidized's `@gitcache` holds stale OID → node mappings, the version history API now supports an `epoch` parameter to read git repository history directly, bypassing Oxidized's in-memory cache. Fixes version history loading failure after device IP changes. |
| **版本历史时间解析修复** - 前端 Dashboard 的 `viewVersionHistory()` 函数现在先将 `v.time` 的 ISO 时间字符串转换为 Unix epoch（`Math.floor(new Date(v.time).getTime() / 1000)`）再调用 API，解决了时间参数传递错误导致的版本历史加载失败问题。 | **Version History Time Parsing Fix** - The Dashboard's `viewVersionHistory()` function now converts `v.time` ISO string to Unix epoch (`Math.floor(new Date(v.time).getTime() / 1000)`) before calling the API, fixing version history loading failures caused by incorrect time parameter formatting. |
| **登出重定向修复** - 修复 `auth.py` 中 `logout()` 函数重定向到硬编码 `/login` 路径而非 Flask Blueprint `pages.login` 的问题，现在正确使用 `redirect(url_for('pages.login'))`。 | **Logout Redirect Fix** - Fixed `logout()` in `auth.py` redirecting to hardcoded `/login` path instead of Flask Blueprint `pages.login`; now correctly uses `redirect(url_for('pages.login'))`. |

### 🔧 改进 / Improvements

| 中文 | English |
|------|---------|
| **移除华为 SSH Input 脚本** - 删除了 `oxidized-config/input/huaweissh.rb`，改用 `oxidized-config/model/huawei.rb` 统一处理，简化架构 | **Removed Huawei SSH Input Script** - Deleted `oxidized-config/input/huaweissh.rb`, now using `oxidized-config/model/huawei.rb` for unified handling, simplifying architecture |
| **Nginx 配置增强** - `nginx-proxy.conf` 新增 gzip 压缩（gzip_types: text/plain text/css application/json application/javascript text/xml application/xml） | **Nginx Config Enhancement** - `nginx-proxy.conf` added gzip compression (gzip_types: text/plain text/css application/json application/javascript text/xml application/xml) |
| **数据库模块化** - `database.py` 中 `ensure_csv_synced()` 保留，新增 `init_database()` 数据库初始化 | **Database Modularization** - `database.py` keeps `ensure_csv_synced()`, adds `init_database()` for database initialization |
| **Routes 蓝图注册** - `routes/__init__.py` 中注册所有新增蓝图（pages, groups_api, credentials_api, models_api, config_api） | **Routes Blueprint Registration** - `routes/__init__.py` registers all new blueprints (pages, groups_api, credentials_api, models_api, config_api) |
| **Huawei Model 增强** - `oxidized-config/model/huawei.rb` 增强，移除 input 依赖，统一使用 model | **Huawei Model Enhancement** - `oxidized-config/model/huawei.rb` enhanced, removed input dependency, unified to use model |

### 📝 文档 / Documentation

| 中文 | English |
|------|---------|
| 所有 README 文件添加完整更新日志 | All README files updated with full changelog |
| README.md 添加架构图、故障排除章节 | README.md added architecture diagram, troubleshooting section |
| 添加版本历史 OID cache stale 问题说明 | Added version history OID cache stale issue description |

---

## v1.2.1 (2026-04-23) 🔒 安全修复 / 🔒 Security Fix

> **修复 GitHub Code Scanning 告警** - 共修复 18 处 `py/stack-trace-exposure` 漏洞。
> **Fixed GitHub Code Scanning Alerts** - Fixed 18 instances of `py/stack-trace-exposure` vulnerability.

### 🔒 安全修复 / Security Fixes

| 中文 | English |
|------|---------|
| **修复 API 错误信息泄露** - 替换所有 `except Exception as e: return ... str(e)` 为通用错误消息 `"Internal server error"` 或 `"Failed to create user"`，防止异常堆栈信息暴露给 API 客户端。修复 CWE-209/CWE-497（通过错误消息的信息泄露）。涉及文件：`config_api.py`（11处）、`auth.py`（2处）、`nodes.py`（2处）、`groups_api.py`（3处）。 | **Fixed API Error Information Exposure** - Replaced all `except Exception as e: return ... str(e)` with generic error messages `"Internal server error"` or `"Failed to create user"`, preventing exception stack traces from being exposed to API clients. Fixes CWE-209/CWE-497 (Information exposure through error messages). Files affected: `config_api.py` (11 instances), `auth.py` (2 instances), `nodes.py` (2 instances), `groups_api.py` (3 instances). |

---

## v1.0.0 (2026-01-10)

| 中文 | English |
|------|---------|
| 初始版本发布 | Initial release |
| 节点管理与状态监控 | Node management and status monitoring |
| 配置版本对比 | Configuration version comparison |
| 凭证管理 | Credential management |
| 自研华为设备型号支持 | Custom Huawei device model support |
