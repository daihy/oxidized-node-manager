# Oxidized Node Manager

[English](README_en.md) | [中文](README_zh.md)

---

## 选择语言 / Select Language

- [English Version](README_en.md)
- [中文版本](README_zh.md)

---

## Features / 功能特性

### English

**Oxidized Node Manager** is a network device configuration backup management system built on Oxidized, providing a Web UI for node management and status monitoring.

- **Node Management** - Add, edit, delete network device nodes
- **Real-time Status Monitoring** - View Oxidized backup status and history
- **Configuration Comparison** - View device configuration version differences
- **Credential Management** - Centralized management of device access credentials
- **Model Management** - Support for 100+ network device models
- **One-click Restart** - Restart Oxidized container via UI to load new configuration
- **Custom Huawei Support** - Built-in `huawei.rb` model and `huaweissh.rb` input scripts with proprietary features for Huawei VRP devices

### 中文

**Oxidized Node Manager** 是一个网络设备配置备份管理系统，基于 Oxidized 构建，提供 Web UI 进行节点管理和状态监控。

- **节点管理** - 添加、编辑、删除网络设备节点
- **实时状态监控** - 查看 Oxidized 备份状态和历史
- **配置对比** - 查看设备配置版本差异
- **凭证管理** - 集中管理设备访问凭据
- **型号管理** - 支持 100+ 网络设备型号
- **一键重启** - 通过 UI 重启 Oxidized 容器加载新配置
- **华为设备深度支持** - 内置自研 `huawei.rb` 型号和 `huaweissh.rb` 输入脚本，支持华为 VRP 设备特性

---

## Custom Huawei Device Support / 华为设备深度支持

### English

This project includes **custom-developed `huawei.rb` model and `huaweissh.rb` input scripts** that solve compatibility issues with legacy Huawei devices:

- **Non-standard SSH port support** (e.g., port 32410)
- **Legacy Huawei SSH** - Uses `diffie-hellman-group-exchange-sha1` algorithm for older devices
- **Pagination handling** - Auto-filters `---- More ----` prompts
- **Screen-length disabling** - Executes `screen-length 0 temporary` automatically
- **120-second timeout** - Waits for complete configuration before disconnecting

Compatible with Huawei VRP devices: S Series switches (S5700, S6700, S9700), AR routers, AC controllers, and more.

See [README_en.md](README_en.md) for full details.

### 中文

本项目包含**自研的 `huawei.rb` 型号和 `huaweissh.rb` 输入脚本**，解决老款华为设备兼容性问题：

- **非标准 SSH 端口支持**（如 32410 端口）
- **老款华为 SSH** - 使用 `diffie-hellman-group-exchange-sha1` 算法
- **分页处理** - 自动过滤 `---- More ----` 提示
- **屏幕长度禁用** - 自动执行 `screen-length 0 temporary`
- **120 秒超时** - 等待完整配置输出后再断开

兼容华为 VRP 设备：S 系列交换机（S5700、S6700、S9700）、AR 路由器、AC 控制器等。

详情见 [README_zh.md](README_zh.md)。

---

## Quick Links / 快速链接

| Document / 文档 | Description / 描述 |
|---------------|-------------------|
| [README_en.md](README_en.md) | English Documentation |
| [README_zh.md](README_zh.md) | 中文文档 |

---

## Getting Started / 开始使用

### English

```bash
# Clone the repository
git clone https://github.com/daihy/oxidized-node-manager.git
cd oxidized-node-manager

# Deploy with one command
chmod +x package_deploy.sh
sudo ./package_deploy.sh
```

### 中文

```bash
# 克隆仓库
git clone https://github.com/daihy/oxidized-node-manager.git
cd oxidized-node-manager

# 一键部署
chmod +x package_deploy.sh
sudo ./package_deploy.sh
```

---

## License / 许可证

MIT License

## Links / 链接

- [Oxidized](https://github.com/ytti/oxidized)
- [Flask](https://flask.palletsprojects.com/)
- [Docker](https://docs.docker.com/)
