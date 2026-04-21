# Oxidized Node Manager

[English](README_en.md) | [中文](README_zh.md)

---

## 选择语言 / Select Language

- [English Version](README_en.md)
- [中文版本](README_zh.md)

---

## 更新日志 / Changelog

> 📋 **完整更新日志请查看 [CHANGELOG.md](CHANGELOG.md)**

### v1.2.0 (2026-04-21) ⚠️ 重大升级

> **🔴 核心重构**：本次更新包含程序架构重构、UI 完全重写、新增多个 API 模块。

#### 🚀 新增功能

- **前端完全重构** - `app.py` 3000+ 行内联模板 → `templates/` + `static/` 独立目录
- **新增 Groups/Credentials/Models/Config API** - 设备分组、凭证、型号、配置管理接口
- **新增 Pages Blueprint** - 独立页面路由蓝图
- **新增 Config Service** - Oxidized 配置业务逻辑层

#### 🐛 错误修复

- **Oxidized OID 缓存 stale 问题修复** - 新增 `epoch` 参数直接读取 git 仓库，绕过 Oxidized 内存缓存
- **版本历史时间解析修复** - Dashboard 将 ISO 时间转换为 Unix epoch 再调用 API
- **登出重定向修复** - `redirect(url_for('pages.login'))` 替代硬编码 `/login`

#### 🔧 改进

- 移除 `huaweissh.rb`，统一使用 `model/huawei.rb`
- `nginx-proxy.conf` 新增 gzip 压缩
- 所有 README 文件添加完整更新日志

### v1.0.0 (2026-01-10)

- 初始版本发布
- 节点管理与状态监控
- 配置版本对比
- 凭证管理
- 自研华为设备型号支持

---

## 功能特性 / Features

### English

**Oxidized Node Manager** is a network device configuration backup management system built on Oxidized, providing a Web UI for node management and status monitoring.

- **Node Management** - Add, edit, delete network device nodes
- **Real-time Status Monitoring** - View Oxidized backup status and history
- **Configuration Comparison** - View device configuration version differences
- **Credential Management** - Centralized management of device access credentials
- **Model Management** - Support for 100+ network device models
- **One-click Restart** - Restart Oxidized container via UI to load new configuration
- **Custom Huawei Support** - Built-in `huawei.rb` model with proprietary features for Huawei VRP devices

### 中文

**Oxidized Node Manager** 是一个网络设备配置备份管理系统，基于 Oxidized 构建，提供 Web UI 进行节点管理和状态监控。

- **节点管理** - 添加、编辑、删除网络设备节点
- **实时状态监控** - 查看 Oxidized 备份状态和历史
- **配置对比** - 查看设备配置版本差异
- **凭证管理** - 集中管理设备访问凭据
- **型号管理** - 支持 100+ 网络设备型号
- **一键重启** - 通过 UI 重启 Oxidized 容器加载新配置
- **华为设备深度支持** - 内置自研 `huawei.rb` 型号，支持华为 VRP 设备特性

---

## 系统架构 / System Architecture

### English

```
┌─────────────────┐     ┌─────────────────┐
│   Browser       │────▶│  nginx-proxy    │
│   :8080        │◀────│                 │
└─────────────────┘     └────────┬────────┘
                                │
                    ┌──────────┴──────────┐
                    │                     │
              ┌─────▼─────┐        ┌──────▼──────┐
              │Node Manager│        │  Oxidized   │
              │  (Flask)   │◀──────▶│  (Backup)   │
              │   :5000    │        │    :8888    │
              └─────┬─────┘        └──────┬──────┘
                    │                     │
                    │            ┌────────┴────────┐
                    │            │  SQLite DB       │
                    │            │  (nodes.db)      │
                    │            └────────────────┘
                    │
          ┌─────────┴─────────┐
          │/var/run/docker.sock│
          └───────────────────┘
```

### 中文

```
┌─────────────────┐     ┌─────────────────┐
│   浏览器         │────▶│  nginx-proxy    │
│   :8080        │◀────│                 │
└─────────────────┘     └────────┬────────┘
                                 │
                     ┌──────────┴──────────┐
                     │                     │
               ┌─────▼─────┐        ┌──────▼──────┐
               │Node Manager│        │  Oxidized   │
               │  (Flask)   │◀──────▶│  (备份)      │
               │   :5000    │        │    :8888    │
               └─────┬─────┘        └──────┬──────┘
                     │                     │
                     │            ┌────────┴────────┐
                     │            │  SQLite 数据库   │
                     │            │  (nodes.db)     │
                     │            └────────────────┘
                     │
          ┌─────────┴─────────┐
          │/var/run/docker.sock│
          └───────────────────┘
```

---

## 项目结构 / Project Structure

```
oxidized-node-manager/
├── docker-compose-oxidized.yml   # Docker Compose 配置
├── nginx-proxy.conf              # Nginx 反向代理配置（含 gzip）
├── package_deploy.sh            # 一键部署脚本
├── .env.template                # 环境变量模板
│
├── node_manager/                # Flask Web 应用
│   ├── app.py                   # 主应用入口
│   ├── database.py              # SQLite 数据库操作
│   ├── config.py                # 配置模块
│   ├── models/                  # 数据模型
│   │   ├── node.py             # 节点模型
│   │   ├── user.py             # 用户模型（bcrypt 认证）
│   │   └── group.py            # 设备分组模型（v1.2.0 新增）
│   ├── routes/                  # Flask 蓝图
│   │   ├── auth.py             # 认证与用户管理
│   │   ├── nodes.py            # 节点 CRUD 操作
│   │   ├── oxidized_api.py     # Oxidized API 集成
│   │   ├── pages.py            # 页面路由蓝图（v1.2.0 新增）
│   │   ├── config_api.py       # Oxidized 配置 API（v1.2.0 新增）
│   │   ├── credentials_api.py  # 设备凭证 API（v1.2.0 新增）
│   │   ├── groups_api.py       # 设备分组 API（v1.2.0 新增）
│   │   └── models_api.py       # 设备型号 API（v1.2.0 新增）
│   ├── services/                # 业务逻辑服务
│   │   ├── docker_service.py   # Docker 容器操作
│   │   ├── oxidized_service.py # Oxidized API 客户端
│   │   └── config_service.py  # Oxidized 配置服务（v1.2.0 新增）
│   ├── static/                  # 静态资源（v1.2.0 重构）
│   │   ├── css/
│   │   │   ├── dashboard.css
│   │   │   ├── login.css
│   │   │   └── force_change_password.css
│   │   └── js/
│   │       ├── dashboard.js     # Dashboard 逻辑（v1.2.0 新增）
│   │       └── i18n.js          # 国际化支持（v1.2.0 新增）
│   ├── templates/               # HTML 模板（v1.2.0 重构）
│   │   ├── dashboard.html
│   │   ├── login.html
│   │   └── force_change_password.html
│   └── tests/                   # 单元测试（pytest）
│
└── oxidized-config/             # Oxidized 配置
    ├── config                   # Oxidized 主配置
    ├── credentials.json        # 设备凭据
    ├── models.json              # 启用的设备型号
    ├── nodes.db                # SQLite 数据库
    ├── input/                   # 自定义输入脚本（预留）
    └── model/                   # 自定义型号脚本
        └── huawei.rb            # 华为型号
```

---

## 快速部署 / Quick Deployment

### 一键部署（推荐）/ One-click Deployment (Recommended)

```bash
# 1. 下载并解压部署包
unzip oxidized-node-manager.zip
cd oxidized-node-manager

# 2. 设置执行权限
chmod +x package_deploy.sh

# 3. 运行部署脚本
sudo ./package_deploy.sh
```

### 手动部署 / Manual Deployment

```bash
# 1. 安装 Docker
curl -fsSL https://get.docker.com | sh

# 2. 创建目录
mkdir -p /opt/oxidized-node-manager
cd /opt/oxidized-node-manager

# 3. 复制文件
cp -r /path/to/deployment-package/* .

# 4. 配置环境变量
cp .env.template .env
nano .env  # 修改密码

# 5. 启动服务
docker-compose up -d
```

---

## 访问地址 / Access Addresses

| 服务 / Service | 地址 / Address | 说明 / Description |
|---------------|---------------|-------------------|
| Node Manager UI | http://IP:8080 | 节点管理界面 / Node management interface |
| Oxidized API | http://IP:8888 | Oxidized API |
| Oxidized Web | http://IP:8888 | Oxidized Web UI |

---

## 默认账号 / Default Accounts

### Node Manager（Flask Web UI）- http://IP:8080

- 用户名 / Username: `admin`
- 密码 / Password: `ADMIN_DEFAULT_PASSWORD` 环境变量（默认 `admin123`）
- **首次登录必须修改密码 / Mandatory password change on first login**
- 存储在 SQLite 数据库 `oxidized-config/nodes.db` 的 users 表中

### Oxidized Web UI - http://IP:8888

- 用户名 / Username: `.env` 中的 `OXIDIZED_USER`（默认 admin）
- 密码 / Password: `.env` 中的 `OXIDIZED_PASSWORD`

> **重要提示 / Important**: 首次部署后请立即修改默认密码！/ Please change default passwords immediately after first deployment!

---

## 常用命令 / Common Commands

```bash
# 进入部署目录 / Enter deployment directory
cd /opt/oxidized-node-manager

# 查看容器状态 / View container status
docker-compose ps

# 查看日志 / View logs
docker-compose logs -f
docker-compose logs -f oxidized-node-manager

# 重启服务 / Restart services
docker-compose restart

# 停止服务 / Stop services
docker-compose down

# 更新代码 / Update code
git pull
docker-compose up -d

# 手动同步 CSV（如需要）/ Manually sync CSV (if needed)
docker exec oxidized-node-manager python -c "from database import ensure_csv_synced; ensure_csv_synced()"
```

---

## 数据备份 / Data Backup

需要备份的关键文件 / Key files to backup:

```bash
# 打包备份 / Package backup
cd /opt/oxidized-node-manager
tar -czvf oxidized-backup-$(date +%Y%m%d).tar.gz \
  oxidized-config/credentials.json \
  oxidized-config/users.json \
  oxidized-config/nodes.db \
  oxidized-config/config

# 备份到远程服务器 / Backup to remote server
scp oxidized-backup-*.tar.gz user@backup-server:/path/to/backups/
```

---

## 数据恢复 / Data Recovery

```bash
# 1. 停止服务 / Stop services
cd /opt/oxidized-node-manager
docker-compose down

# 2. 恢复文件 / Restore files
tar -xzvf oxidized-backup-20240115.tar.gz

# 3. 重启服务 / Restart services
docker-compose up -d
```

---

## 开发 / Development

### 本地开发 / Local Development

```bash
# 1. 进入应用目录 / Enter app directory
cd node_manager

# 2. 安装依赖 / Install dependencies
pip install flask requests bcrypt pytest

# 3. 运行测试 / Run tests
pytest tests/ -v

# 4. 启动开发服务器 / Start development server
python app.py
```

### Docker 开发 / Docker Development

```bash
# 构建并启动 / Build and start
docker-compose up -d

# 查看日志 / View logs
docker-compose logs -f oxidized-node-manager

# 进入容器 / Enter container
docker exec -it oxidized-node-manager /bin/bash
```

---

## 华为设备自定义型号 / Custom Huawei Device Model

### 华为型号功能 / Huawei Model Features

`huawei.rb` 模型集成所有华为设备备份所需功能：

| 功能 / Feature | 说明 / Description |
|--------------|-------------------|
| 非标准 SSH 端口 / Non-standard SSH port | 通过 CSV 配置中的 `vars:ssh_port` 支持 |
| 老款 SSH 算法 / Legacy SSH algorithm | 使用 `diffie-hellman-group-exchange-sha1` 算法 |
| `display version` | 捕获系统版本信息，带 `#` 注释前缀 |
| `display device` | 捕获设备信息，带 `#` 注释前缀 |
| `display current-configuration` | 获取完整运行配置 |
| `screen-length 0 temporary` | 禁用输出分页 |
| `---- More ----` 过滤 | 自动过滤分页提示 |

#### 使用方法 / Usage

在 Node Manager 中添加华为设备时，选择型号 `huawei`，系统将自动使用这些自定义脚本进行配置备份。

#### 兼容设备 / Compatible Devices

华为 VRP（通用路由平台）系统设备：

- S 系列交换机（S5700、S6700、S9700 等）/ S Series switches
- AR 系列路由器 / AR Series routers
- AC 控制器 / AC controllers
- 其他支持 `display current-configuration` 的华为设备

---

## 支持的设备型号 / Supported Device Models

支持 100+ 网络设备型号，包括但不限于 / Support for 100+ network device models, including but not limited to:

- Cisco（IOS、IOS-XE、IOS-XR、NX-OS、ASA、AireOS、Meraki）
- Juniper（JunOS、ScreenOS）
- Huawei（VRP）
- HP/Aruba（ProCurve、Comware）
- Arista（EOS）
- MikroTik（RouterOS）
- Fortinet（FortiOS）
- Palo Alto（PAN-OS）
- Dell、Ubiquiti、VyOS

---

## 故障排除 / Troubleshooting

### 容器无法启动 / Container Cannot Start

```bash
# 查看详细日志 / View detailed logs
docker-compose logs oxidized-node-manager

# 检查端口占用 / Check port usage
netstat -tlnp | grep -E '8080|8888|5000'
```

### Oxidized 备份失败 / Oxidized Backup Failed

```bash
# 检查 Oxidized 配置 / Check Oxidized configuration
docker exec oxidized cat /oxidized_config/config

# 测试 SSH 连接 / Test SSH connection
docker exec oxidized ssh -v -p 22 user@device-ip

# 查看 Oxidized 日志 / View Oxidized logs
docker exec oxidized cat /home/oxidized/.config/oxidized/logs/oxidized.log
```

### CSV 同步异常 / CSV Out of Sync

```bash
# 手动触发同步 / Manually trigger sync
docker exec oxidized-node-manager python -c "from database import ensure_csv_synced; ensure_csv_synced()"

# 查看 CSV 内容 / Check CSV content
docker exec oxidized-node-manager cat /oxidized_config/nodes.csv
```

### 版本历史加载失败（OID Cache Stale）/ Version History Load Failed

> **v1.2.0 已修复** - 当设备 IP 变更后，Oxidized 的 `@gitcache` 可能持有过期的 OID → node 映射，导致版本历史 API 返回错误。v1.2.0 新增 `node_version_by_oid` 接口支持 `epoch` 参数直接读取 git 仓库，不依赖 Oxidized 内存缓存。

如遇此问题，请升级到 v1.2.0 或更高版本。

---

## 安全建议 / Security Recommendations

1. **修改默认密码 / Change default passwords** - 部署后立即修改 `.env` 中的密码
2. **限制端口访问 / Restrict port access** - 生产环境使用防火墙限制 8080/8888 端口
3. **启用 HTTPS / Enable HTTPS** - 使用 nginx 反向代理 + SSL 证书
4. **定期备份 / Regular backup** - 建立备份策略并定期执行备份

---

## 许可证 / License

MIT License

---

## 参考链接 / References

- [Oxidized 官方文档 / Oxidized Official Documentation](https://github.com/ytti/oxidized)
- [Flask 文档 / Flask Documentation](https://flask.palletsprojects.com/)
- [Docker 文档 / Docker Documentation](https://docs.docker.com/)
