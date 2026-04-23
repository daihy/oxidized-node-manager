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

> **修复 GitHub Code Scanning 告警** - 共修复 21 处 `py/stack-trace-exposure` + 1 处 `py/clear-text-logging-sensitive-data` 漏洞。Alert #21 (`py/clear-text-storage-sensitive-data`) 为 Oxidized 设计决策，永久标记为 wontfix。
> **Fixed GitHub Code Scanning Alerts** - Fixed 21 instances of `py/stack-trace-exposure` and 1 instance of `py/clear-text-logging-sensitive-data`. Alert #21 (`py/clear-text-storage-sensitive-data`) is a design decision and permanently marked as wontfix.

### 🔒 安全修复 / Security Fixes

| 中文 | English |
|------|---------|
| **修复 API 错误信息泄露（CWE-209/CWE-497）** - 第一批：替换所有 `except Exception as e: return ... str(e)` 为通用错误消息，防止异常堆栈暴露给 API 客户端。涉及：`config_api.py`（11处）、`auth.py`（2处）、`nodes.py`（2处）、`groups_api.py`（3处）。 | **Fixed API Error Information Exposure (CWE-209/CWE-497) — Batch 1** - Replaced all `except Exception as e: return ... str(e)` with generic error messages. Files: `config_api.py` (11), `auth.py` (2), `nodes.py` (2), `groups_api.py` (3). |
| **修复 API 错误信息泄露（CWE-209/CWE-497）** - 第二批：移除 `except Exception as e:` 中的 `as e` 子句（消除 CodeQL 的 generic Exception 捕获告警模式）；替换 `result["error"]` 为 `"Backup failed"`（`oxidized_api.py`）；替换 `str(e)` 为 `"Backup request failed"`（`oxidized_service.py`）；移除 `print(password)` 明文日志（`database.py`）。 | **Fixed API Error Information Exposure (CWE-209/CWE-497) — Batch 2** - Removed `as e` from `except Exception as e:` blocks; replaced `result["error"]` with `"Backup failed"` (`oxidized_api.py`); replaced `str(e)` with `"Backup request failed"` (`oxidized_service.py`); removed `print(password)` plain-text logging (`database.py`). |
| **修复 YAML 错误信息泄露** - `validate_yaml()` 的 `errors` 字段原本返回 `str(yaml_error)`（暴露 YAML 解析细节），现改为通用消息 `"Invalid YAML configuration"`（`config_service.py`）。 | **Fixed YAML Error Detail Exposure** - `validate_yaml()` was returning `str(yaml_error)` in the `errors` field, exposing YAML parser details to API clients. Now returns generic `"Invalid YAML configuration"` instead (`config_service.py`). |
| **移除明文密码日志** - `database.py` 中的 `print(password)` 调用被移除，防止密码在日志中明文输出。 | **Removed Plain-text Password Logging** - Removed `print(password)` in `database.py` to prevent passwords from appearing in logs. |
| **Alert #21 wontfix** - `py/clear-text-storage-sensitive-data` 告警（`config_service.py`）为 Oxidized 设计决策：配置文件必须存储设备凭据以供 Oxidized 认证使用。详见 `SECURITY.md`。 | **Alert #21 Wontfix** - `py/clear-text-storage-sensitive-data` (`config_service.py`) is a design decision: Oxidized config must store device credentials for authentication. See `SECURITY.md` for rationale and alternative solutions. |

---

## v1.2.2 (2026-04-23) 📝 文档修复 / 📝 Documentation Fix

> **文档修复** — 本次更新修复双语项目文档的完整性和同步问题：SECURITY.md 补全中文版本，README_en.md / README_zh.md 项目结构章节与 README.md 同步。
> **Documentation Fix** — This release fixes bilingual documentation integrity and sync issues: SECURITY.md now has complete Chinese version, README_en.md / README_zh.md project structure sections synced with README.md.

### 📝 文档修复 / Documentation Fixes

| 中文 | English |
|------|---------|
| **SECURITY.md 补全中文版本** — 双语项目所有对外文档必须中英双语，原 SECURITY.md 为纯英文，现补全中文版本，Alert #21、风险评估、替代方案全部中英双语对照。 | **SECURITY.md Added Chinese Version** - Bilingual projects require all对外文档 to be Chinese/English bilingual. Original SECURITY.md was English-only; now added complete Chinese version with Alert #21, risk assessment, and alternative solutions in bilingual table format. |
| **README_en.md 项目结构章节同步** — 新增 v1.2.0 的 `pages.py`、`config_api.py`、`credentials_api.py`、`groups_api.py`、`models_api.py`、`config_service.py`、`group.py`、`static/`、`templates/` 等文件描述。 | **README_en.md Project Structure Synced** - Added missing v1.2.0 files: `pages.py`, `config_api.py`, `credentials_api.py`, `groups_api.py`, `models_api.py`, `config_service.py`, `group.py`, `static/`, `templates/`. |
| **README_zh.md 项目结构章节同步** — 同上（中文版）。 | **README_zh.md Project Structure Synced** - Same as above (Chinese version). |

---

## v1.0.0 (2026-01-10)

| 中文 | English |
|------|---------|
| 初始版本发布 | Initial release |
| 节点管理与状态监控 | Node management and status monitoring |
| 配置版本对比 | Configuration version comparison |
| 凭证管理 | Credential management |
| 自研华为设备型号支持 | Custom Huawei device model support |
