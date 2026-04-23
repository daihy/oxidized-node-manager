# Security Policy / 安全政策

## Reporting Security Vulnerabilities / 报告安全漏洞

If you discover a security vulnerability, please report it via [GitHub Security Advisories](https://github.com/daihy/oxidized-node-manager/security/advisories/new).

如果您发现安全漏洞，请通过 [GitHub Security Advisories](https://github.com/daihy/oxidized-node-manager/security/advisories/new) 报告。

---

## Known Limitations / 已知限制

### Alert #21: `py/clear-text-storage-sensitive-data` — Oxidized Credential Storage / Oxidized 凭据存储

**Status / 状态**: Acknowledged, not remediated / 已确认，未修复

**Location / 位置**: `node_manager/services/config_service.py:65`

**Rule / 规则**: `py/clear-text-storage-sensitive-data`

**Description / 描述**: The Oxidized configuration file (e.g., `/oxidized_config/config`) stores device credentials (usernames and passwords) in plain text.

Oxidized 配置文件（如 `/oxidized_config/config`）以明文形式存储设备凭据（用户名和密码）。

**Reason for Not Fixing / 不修复原因**: This is a **design decision**, not a vulnerability. Oxidized requires credentials in its native config format to authenticate with network devices during backup operations. Changing this would require a substantial architectural redesign (e.g., integrating a secrets manager such as HashiCorp Vault, AWS Secrets Manager, or Kubernetes Secrets), which is not planned.

这是**设计决策**，而非漏洞。Oxidized 需要在其原生配置格式中存储凭据，以便在备份操作期间对网络设备进行身份验证。要改变这一点需要大规模架构重构（例如集成 HashiCorp Vault、AWS Secrets Manager 或 Kubernetes Secrets 等密钥管理器），暂无此计划。

**Risk Assessment / 风险评估**:
- The credentials file is protected by host filesystem permissions (`0600`, owned by the `oxidized` user inside the container).
- The file is **not** exposed via the Node Manager web API or any HTTP endpoint.
- It is **not** committed to the Git repository (`.gitignore` excludes `oxidized-config/credentials.json` and `oxidized-config/config`).
- Access to the credentials file requires shell access to the host or container.

- 凭据文件受主机文件系统权限保护（`0600`，由容器内的 `oxidized` 用户拥有）。
- 该文件**不会**通过 Node Manager Web API 或任何 HTTP 端点对外暴露。
- 该文件**不会**提交到 Git 仓库（`.gitignore` 排除了 `oxidized-config/credentials.json` 和 `oxidized-config/config`）。
- 访问凭据文件需要主机或容器的 shell 权限。

**Alternative Solutions / 替代方案** (not implemented / 未实现):

1. **Secrets Manager Integration / 密钥管理器集成**: Store credentials in HashiCorp Vault, AWS Secrets Manager, or similar. Oxidized would retrieve credentials at runtime. This requires significant development effort and operational overhead.

   将凭据存储在 HashiCorp Vault、AWS Secrets Manager 或类似服务中。Oxidized 在运行时获取凭据。这需要大量的开发工作和运维开销。

2. **Encrypted Config File / 加密配置文件**: Use GPG or age encryption for the config file, with the decryption key injected at container startup. Oxidized would need modification to support encrypted configs.

   使用 GPG 或 age 加密配置文件，在容器启动时注入解密密钥。Oxidized 需要修改以支持加密配置。

3. **Credential API / 凭据 API**: Add a credential retrieval API endpoint that fetches from a secrets manager and passes to Oxidized. Requires additional infrastructure.

   添加凭据获取 API 端点，从密钥管理器获取并传递给 Oxidized。需要额外的基础设施。

**Recommendation / 建议**: For production deployments, ensure:

生产环境部署建议：

- Host firewall restricts access to the Docker socket and container files.
  主机防火墙限制对 Docker socket 和容器文件的访问。
- Container runtime uses read-only root filesystems where possible.
  容器运行时尽可能使用只读根文件系统。
- Regular rotation of device credentials as a compensating control.
  定期轮换设备凭据作为补偿控制措施。

---

## Code Scanning Alerts / 代码扫描告警

This project uses GitHub CodeQL scanning. See [GitHub Security > Code Scanning](https://github.com/daihy/oxidized-node-manager/security/code-scanning) for the full alert list.

本项目使用 GitHub CodeQL 扫描。完整的告警列表请参阅 [GitHub Security > Code Scanning](https://github.com/daihy/oxidized-node-manager/security/code-scanning)。

All `py/stack-trace-exposure` alerts (CWE-209/CWE-497) have been fixed. The `py/clear-text-storage-sensitive-data` alert above is the only remaining open alert and is intentionally left open as explained above.

所有 `py/stack-trace-exposure` 告警（CWE-209/CWE-497）均已修复。上述 `py/clear-text-storage-sensitive-data` 告警是唯一剩余的开放告警，已按上述说明故意保留。
