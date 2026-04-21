# Oxidized Node Manager

Network device configuration backup management system, built on Oxidized, providing Web UI for node management and status monitoring.

## Changelog

### v1.1.0 (2026-01-xx)

#### Bug Fixes

- **Oxidized OID Cache Stale Fix** - When Oxidized's `@gitcache` holds stale OID → node mappings, the version history API now supports an `epoch` parameter to read git repository history directly, bypassing Oxidized's in-memory cache. Fixes the issue where version history fails to load after device IP changes.
- **Version History Time Parsing Fix** - The Dashboard frontend now converts ISO time strings to Unix epoch before calling the API, fixing version history loading failures caused by incorrect time parameter formatting.
- **Logout Redirect Fix** - Fixed logout redirecting to hardcoded `/login` path instead of Flask Blueprint `pages.login`; now correctly uses `redirect(url_for('pages.login'))`.

#### New Features

- **Fetch Version Config by OID + Epoch** - New `GET /api/oxidized/node_version_by_oid` endpoint accepts `oid` and `epoch` parameters to directly read the config file at a specific timestamp from the git repository, bypassing Oxidized's OID cache.

#### Improvements

- **Removed Huawei SSH Input Script** - Deleted `oxidized-config/input/huaweissh.rb`, now using `oxidized-config/model/huawei.rb` for unified handling, simplifying the architecture.

### v1.0.0 (2026-01-10)

- Initial release
- Node management and status monitoring
- Configuration version comparison
- Credential management
- Custom Huawei device model support

---

## Features

- **Node Management** - Add, edit, delete network device nodes
- **Real-time Status Monitoring** - View Oxidized backup status and history
- **Configuration Comparison** - View device configuration version differences
- **Credential Management** - Centralized management of device access credentials
- **Model Management** - Support for 100+ network device models
- **One-click Restart** - Restart Oxidized container via UI to load new configuration

## System Architecture

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

## Project Structure

```
oxidized-node-manager/
├── docker-compose-oxidized.yml   # Docker Compose configuration
├── nginx-proxy.conf              # Nginx reverse proxy configuration
├── package_deploy.sh            # One-click deployment script
├── .env.template                # Environment variables template
│   │
├── node_manager/                # Flask Web Application
│   ├── app.py                   # Main application entry
│   ├── database.py              # SQLite database operations
│   ├── config.py                # Configuration module
│   ├── models/                  # Data models
│   │   ├── node.py             # Node model
│   │   └── user.py             # User model with bcrypt auth
│   ├── routes/                  # Flask blueprints
│   │   ├── auth.py             # Authentication & user management
│   │   ├── nodes.py            # Node CRUD operations
│   │   └── oxidized_api.py     # Oxidized API integration
│   ├── services/                # Business logic services
│   │   ├── docker_service.py   # Docker container operations
│   │   └── oxidized_service.py # Oxidized API client
│   └── tests/                   # Unit tests (pytest)
│
└── oxidized-config/             # Oxidized Configuration
    ├── config                   # Oxidized main config
    ├── credentials.json        # Device credentials
    ├── models.json              # Enabled device models
    ├── nodes.db                # SQLite database
    ├── input/                   # Custom input scripts (reserved)
    └── model/                   # Custom model scripts
        └── huawei.rb            # Huawei model
```

## Quick Deployment

### One-click Deployment (Recommended)

```bash
# 1. Download and extract deployment package
unzip oxidized-node-manager.zip
cd oxidized-node-manager

# 2. Set execute permissions
chmod +x package_deploy.sh

# 3. Run deployment script
sudo ./package_deploy.sh
```

### Manual Deployment

```bash
# 1. Install Docker
curl -fsSL https://get.docker.com | sh

# 2. Create directory
mkdir -p /opt/oxidized-node-manager
cd /opt/oxidized-node-manager

# 3. Copy files
cp -r /path/to/deployment-package/* .

# 4. Configure environment variables
cp .env.template .env
nano .env  # Modify passwords

# 5. Start services
docker-compose up -d
```

## Access Addresses

| Service | Address | Description |
|---------|---------|------------|
| Node Manager UI | http://IP:8080 | Node management interface |
| Oxidized API | http://IP:8888 | Oxidized API |
| Oxidized Web | http://IP:8888 | Oxidized Web UI |

## Default Accounts

### Node Manager (Flask Web UI) - http://IP:8080

- Username: `admin`
- Password: `ADMIN_DEFAULT_PASSWORD` env var (default `admin123`)
- **Mandatory password change on first login**
- Stored in SQLite database `oxidized-config/nodes.db` users table

### Oxidized Web UI - http://IP:8888

- Username: `OXIDIZED_USER` in `.env` (default admin)
- Password: `OXIDIZED_PASSWORD` in `.env`

> **Important:** Please change default passwords immediately after first deployment!

## Common Commands

```bash
# Enter deployment directory
cd /opt/oxidized-node-manager

# View container status
docker-compose ps

# View logs
docker-compose logs -f
docker-compose logs -f oxidized-node-manager

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Update code
git pull
docker-compose up -d

# Manually sync CSV (if needed)
docker exec oxidized-node-manager python -c "from database import ensure_csv_synced; ensure_csv_synced()"
```

## Data Backup

Key files to backup:

```bash
# Package backup
cd /opt/oxidized-node-manager
tar -czvf oxidized-backup-$(date +%Y%m%d).tar.gz \
  oxidized-config/credentials.json \
  oxidized-config/users.json \
  oxidized-config/nodes.db \
  oxidized-config/config

# Backup to remote server
scp oxidized-backup-*.tar.gz user@backup-server:/path/to/backups/
```

## Data Recovery

```bash
# 1. Stop services
cd /opt/oxidized-node-manager
docker-compose down

# 2. Restore files
tar -xzvf oxidized-backup-20240115.tar.gz

# 3. Restart services
docker-compose up -d
```

## Development

### Local Development

```bash
# 1. Enter app directory
cd node_manager

# 2. Install dependencies
pip install flask requests bcrypt pytest

# 3. Run tests
pytest tests/ -v

# 4. Start development server
python app.py
```

### Docker Development

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f oxidized-node-manager

# Enter container
docker exec -it oxidized-node-manager /bin/bash
```

## Custom Huawei Device Model

The system provides custom Model and Input scripts for Huawei network devices.

### Huawei Model (`oxidized-config/model/huawei.rb`)

Oxidized model definition for Huawei devices, parsing command-line output format:

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

#### Features

| Feature | Description |
|---------|-------------|
| `prompt` | Match Huawei device prompt format `<XXX>` |
| `display current-configuration` | Get complete running configuration |
| `screen-length 0 temporary` | Disable output pagination |
| `---- More ----` filter | Auto-filter pagination prompt |
| `pre_logout "quit"` | Execute quit before logout |

### Huawei Model Features

The `huawei.rb` model integrates all necessary features for Huawei device backup:

| Feature | Description |
|--------|-------------|
| Non-standard SSH port | Support via `vars:ssh_port` in CSV configuration |
| Legacy SSH algorithm | Uses `diffie-hellman-group-exchange-sha1` for older devices |
| `display version` | Captures system version info with `#` comment prefix |
| `display device` | Captures device info with `#` comment prefix |
| `display current-configuration` | Gets complete running configuration |
| `screen-length 0 temporary` | Disables output pagination |
| `---- More ----` filter | Auto-filters pagination prompts |

### Usage

When adding a Huawei device in Node Manager, select model `huawei`, and the system will automatically use these custom scripts for configuration backup.

### Compatible Devices

Huawei VRP (Versatile Routing Platform) system devices:

- S Series switches (S5700, S6700, S9700, etc.)
- AR Series routers
- AC controllers
- Other Huawei devices supporting `display current-configuration`

## Supported Device Models

Support for 100+ network device models, including but not limited to:

- Cisco (IOS, IOS-XE, IOS-XR, NX-OS, ASA, AireOS, Meraki)
- Juniper (JunOS, ScreenOS)
- Huawei (VRP)
- HP/Aruba (ProCurve, Comware)
- Arista (EOS)
- MikroTik (RouterOS)
- Fortinet (FortiOS)
- Palo Alto (PAN-OS)
- Dell, Ubiquiti, VyOS

## Troubleshooting

### Container Cannot Start

```bash
# View detailed logs
docker-compose logs oxidized-node-manager

# Check port usage
netstat -tlnp | grep -E '8080|8888|5000'
```

### Oxidized Backup Failed

```bash
# Check Oxidized configuration
docker exec oxidized cat /oxidized_config/config

# Test SSH connection
docker exec oxidized ssh -v -p 22 user@device-ip

# View Oxidized logs
docker exec oxidized cat /home/oxidized/.config/oxidized/logs/oxidized.log
```

### CSV Out of Sync

```bash
# Manually trigger sync
docker exec oxidized-node-manager python -c "from database import ensure_csv_synced; ensure_csv_synced()"

# Check CSV content
docker exec oxidized-node-manager cat /oxidized_config/nodes.csv
```

## Security Recommendations

1. **Change default passwords** - Modify passwords in `.env` immediately after deployment
2. **Restrict port access** - Use firewall to restrict ports 8080/8888 in production
3. **Enable HTTPS** - Use nginx reverse proxy + SSL certificate
4. **Regular backup** - Establish backup strategy and perform regular backups

## License

MIT License

## References

- [Oxidized Official Documentation](https://github.com/ytti/oxidized)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Documentation](https://docs.docker.com/)
