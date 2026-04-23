# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability, please report it via [GitHub Security Advisories](https://github.com/daihy/oxidized-node-manager/security/advisories/new).

---

## Known Limitations

### Alert #21: `py/clear-text-storage-sensitive-data` — Oxidized Credential Storage

**Status**: Acknowledged, not remediated

**Location**: `node_manager/services/config_service.py:65`

**Rule**: `py/clear-text-storage-sensitive-data`

**Description**: The Oxidized configuration file (e.g., `/oxidized_config/config`) stores device credentials (usernames and passwords) in plain text.

**Reason for Not Fixing**: This is a **design decision**, not a vulnerability. Oxidized requires credentials in its native config format to authenticate with network devices during backup operations. Changing this would require a substantial architectural redesign (e.g., integrating a secrets manager such as HashiCorp Vault, AWS Secrets Manager, or Kubernetes Secrets), which is not planned.

**Risk Assessment**:
- The credentials file is protected by host filesystem permissions (`0600`, owned by the `oxidized` user inside the container).
- The file is **not** exposed via the Node Manager web API or any HTTP endpoint.
- It is **not** committed to the Git repository (`.gitignore` excludes `oxidized-config/credentials.json` and `oxidized-config/config`).
- Access to the credentials file requires shell access to the host or container.

**Alternative Solutions** (not implemented):
1. **Secrets Manager Integration**: Store credentials in HashiCorp Vault, AWS Secrets Manager, or similar. Oxidized would retrieve credentials at runtime. This requires significant development effort and operational overhead.
2. **Encrypted Config File**: Use GPG or age encryption for the config file, with the decryption key injected at container startup. Oxidized would need modification to support encrypted configs.
3. **Credential API**: Add a credential retrieval API endpoint that fetches from a secrets manager and passes to Oxidized. Requires additional infrastructure.

**Recommendation**: For production deployments, ensure:
- Host firewall restricts access to the Docker socket and container files.
- Container runtime uses read-only root filesystems where possible.
- Regular rotation of device credentials as a compensating control.

---

## Code Scanning Alerts

This project uses GitHub CodeQL scanning. See [GitHub Security > Code Scanning](https://github.com/daihy/oxidized-node-manager/security/code-scanning) for the full alert list.

All `py/stack-trace-exposure` alerts (CWE-209/CWE-497) have been fixed. The `py/clear-text-storage-sensitive-data` alert above is the only remaining open alert and is intentionally left open as explained above.
