# Oxidized Node Manager

网络设备配置备份管理系统，基于 Oxidized 构建，提供 Web UI 进行节点管理和状态监控。

## 更新日志

> 📋 **完整更新日志请查看 [CHANGELOG.md](CHANGELOG.md)**

### v1.2.0 (2026-04-21) ⚠️ 重大升级

> **🔴 核心重构**：本次更新包含程序架构重构、UI 完全重写、新增多个 API 模块。

#### 🚀 新增功能

- **前端完全重构** - `app.py` 3000+ 行内联模板 → `templates/` + `static/` 独立目录
  - `templates/dashboard.html` - 全新 Dashboard 页面（节点管理、版本历史、配置对比）
  - `templates/login.html` - 独立登录页面
  - `templates/force_change_password.html` - 强制修改密码页面
  - `static/css/*.css` - 独立样式文件
  - `static/js/dashboard.js` (1747行) - Dashboard JavaScript 逻辑
  - `static/js/i18n.js` (557行) - 国际化支持（中英文切换）

- **新增 Groups/Credentials/Models/Config API** - 设备分组、凭证、型号、配置管理接口
- **新增 Pages Blueprint** - `routes/pages.py`
- **新增 Config Service** - `services/config_service.py`
- **新增 Group Model** - `models/group.py`

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

## 功能特性

- **节点管理** - 添加、编辑、删除网络设备节点
- **实时状态监控** - 查看 Oxidized 备份状态和历史
- **配置对比** - 查看设备配置版本差异
- **凭证管理** - 集中管理设备访问凭据
- **型号管理** - 支持 100+ 网络设备型号
- **一键重启** - 通过 UI 重启 Oxidized 容器加载新配置

## 系统架构

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

## 项目结构

```
oxidized-node-manager/
├── docker-compose-oxidized.yml   # Docker Compose 配置
├── nginx-proxy.conf              # Nginx 反向代理配置
├── package_deploy.sh            # 一键部署脚本
├── .env.template                # 环境变量模板
│
├── node_manager/                # Flask Web 应用
│   ├── app.py                   # 主应用入口
│   ├── database.py              # SQLite 数据库操作
│   ├── config.py                # 配置模块
│   ├── models/                  # 数据模型
│   │   ├── node.py             # 节点模型
│   │   └── user.py             # 用户模型（bcrypt 认证）
│   ├── routes/                  # Flask 蓝图
│   │   ├── auth.py             # 认证与用户管理
│   │   ├── nodes.py            # 节点 CRUD 操作
│   │   └── oxidized_api.py     # Oxidized API 集成
│   ├── services/                # 业务逻辑服务
│   │   ├── docker_service.py   # Docker 容器操作
│   │   └── oxidized_service.py # Oxidized API 客户端
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

## 快速部署

### 一键部署（推荐）

```bash
# 1. 下载并解压部署包
unzip oxidized-node-manager.zip
cd oxidized-node-manager

# 2. 设置执行权限
chmod +x package_deploy.sh

# 3. 运行部署脚本
sudo ./package_deploy.sh
```

### 手动部署

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

## 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| Node Manager UI | http://IP:8080 | 节点管理界面 |
| Oxidized API | http://IP:8888 | Oxidized API |
| Oxidized Web | http://IP:8888 | Oxidized Web UI |

## 默认账号

### Node Manager（Flask Web UI）- http://IP:8080

- 用户名：`admin`
- 密码：`ADMIN_DEFAULT_PASSWORD` 环境变量（默认 `admin123`）
- **首次登录必须修改密码**
- 存储在 SQLite 数据库 `oxidized-config/nodes.db` 的 users 表中

### Oxidized Web UI - http://IP:8888

- 用户名：`.env` 中的 `OXIDIZED_USER`（默认 admin）
- 密码：`.env` 中的 `OXIDIZED_PASSWORD`

> **重要提示：** 首次部署后请立即修改默认密码！

## 常用命令

```bash
# 进入部署目录
cd /opt/oxidized-node-manager

# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f
docker-compose logs -f oxidized-node-manager

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新代码
git pull
docker-compose up -d

# 手动同步 CSV（如需要）
docker exec oxidized-node-manager python -c "from database import ensure_csv_synced; ensure_csv_synced()"
```

## 数据备份

需要备份的关键文件：

```bash
# 打包备份
cd /opt/oxidized-node-manager
tar -czvf oxidized-backup-$(date +%Y%m%d).tar.gz \
  oxidized-config/credentials.json \
  oxidized-config/users.json \
  oxidized-config/nodes.db \
  oxidized-config/config

# 备份到远程服务器
scp oxidized-backup-*.tar.gz user@backup-server:/path/to/backups/
```

## 数据恢复

```bash
# 1. 停止服务
cd /opt/oxidized-node-manager
docker-compose down

# 2. 恢复文件
tar -xzvf oxidized-backup-20240115.tar.gz

# 3. 重启服务
docker-compose up -d
```

## 开发

### 本地开发

```bash
# 1. 进入应用目录
cd node_manager

# 2. 安装依赖
pip install flask requests bcrypt pytest

# 3. 运行测试
pytest tests/ -v

# 4. 启动开发服务器
python app.py
```

### Docker 开发

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f oxidized-node-manager

# 进入容器
docker exec -it oxidized-node-manager /bin/bash
```

## 华为设备自定义型号

系统为华为网络设备提供了自定义 Model 和 Input 脚本。

### 华为型号（`oxidized-config/model/huawei.rb`）

华为设备的 Oxidized 型号定义，解析命令行输出格式：

```ruby
class Huawei < Oxidized::Model
  prompt /^<.*>$/
  comment "# "

  cmd 'display current-configuration' do |cfg|
    lines = cfg.each_line.reject { |line| line =~ /---- More ----/ }.join
    lines
  end

  cfg :ssh do
    post_login "screen-length 0 temporary"
    pre_logout "quit"
  end
end
```

#### 功能特性

| 功能 | 说明 |
|------|------|
| `prompt` | 匹配华为设备提示符格式 `<XXX>` |
| `display current-configuration` | 获取完整运行配置 |
| `screen-length 0 temporary` | 禁用输出分页 |
| `---- More ----` 过滤 | 自动过滤分页提示 |
| `pre_logout "quit"` | 登出前执行 quit |

### 华为型号功能

`huawei.rb` 模型集成所有华为设备备份所需功能：

| 功能 | 说明 |
|------|------|
| 非标准 SSH 端口 | 通过 CSV 配置中的 `vars:ssh_port` 支持 |
| 老款 SSH 算法 | 使用 `diffie-hellman-group-exchange-sha1` 算法 |
| `display version` | 捕获系统版本信息，带 `#` 注释前缀 |
| `display device` | 捕获设备信息，带 `#` 注释前缀 |
| `display current-configuration` | 获取完整运行配置 |
| `screen-length 0 temporary` | 禁用输出分页 |
| `---- More ----` 过滤 | 自动过滤分页提示 |

#### 使用方法

在 Node Manager 中添加华为设备时，选择型号 `huawei`，系统将自动使用这些自定义脚本进行配置备份。

#### 兼容设备

华为 VRP（通用路由平台）系统设备：

- S 系列交换机（S5700、S6700、S9700 等）
- AR 系列路由器
- AC 控制器
- 其他支持 `display current-configuration` 的华为设备

## 支持的设备型号

支持 100+ 网络设备型号，包括但不限于：

- Cisco（IOS、IOS-XE、IOS-XR、NX-OS、ASA、AireOS、Meraki）
- Juniper（JunOS、ScreenOS）
- Huawei（VRP）
- HP/Aruba（ProCurve、Comware）
- Arista（EOS）
- MikroTik（RouterOS）
- Fortinet（FortiOS）
- Palo Alto（PAN-OS）
- Dell、Ubiquiti、VyOS

## 故障排除

### 容器无法启动

```bash
# 查看详细日志
docker-compose logs oxidized-node-manager

# 检查端口占用
netstat -tlnp | grep -E '8080|8888|5000'
```

### Oxidized 备份失败

```bash
# 检查 Oxidized 配置
docker exec oxidized cat /oxidized_config/config

# 测试 SSH 连接
docker exec oxidized ssh -v -p 22 user@device-ip

# 查看 Oxidized 日志
docker exec oxidized cat /home/oxidized/.config/oxidized/logs/oxidized.log
```

### CSV 同步异常

```bash
# 手动触发同步
docker exec oxidized-node-manager python -c "from database import ensure_csv_synced; ensure_csv_synced()"

# 查看 CSV 内容
docker exec oxidized-node-manager cat /oxidized_config/nodes.csv
```

## 安全建议

1. **修改默认密码** - 部署后立即修改 `.env` 中的密码
2. **限制端口访问** - 生产环境使用防火墙限制 8080/8888 端口
3. **启用 HTTPS** - 使用 nginx 反向代理 + SSL 证书
4. **定期备份** - 建立备份策略并定期执行备份

## 许可证

MIT 许可证

## 参考链接

- [Oxidized 官方文档](https://github.com/ytti/oxidized)
- [Flask 文档](https://flask.palletsprojects.com/)
- [Docker 文档](https://docs.docker.com/)
