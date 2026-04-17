#!/bin/bash
#
# Oxidized Node Manager - One-click Deployment Script
# Supports bilingual output (English/Chinese)
#

set -e

# ==================== Configuration ====================

# Language setting (default: English)
LANG="${LANG:-en}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --lang|--language)
            LANG="$2"
            shift 2
            ;;
        --lang=*|--language=*)
            LANG="${1#*=}"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--lang=en|zh]"
            echo ""
            echo "Options:"
            echo "  --lang, --language  Set language (en: English, zh: Chinese) [default: en]"
            echo "  -h, --help          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--lang=en|zh]"
            exit 1
            ;;
    esac
done

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="oxidized-node-manager"
PROJECT_DIR="/opt/oxidized-node-manager"
BACKUP_DIR="/opt/oxidized-backup"

# ==================== Bilingual Messages ====================

# Array-based bilingual messages
declare -A MSG

# General
MSG['script_title']="Oxidized Node Manager - One-click Deployment"
MSG['script_title_zh']="Oxidized Node Manager - 一键部署脚本"
MSG['checking_env']="Checking environment..."
MSG['checking_env_zh']="检查环境..."
MSG['deploy_dir']="Creating deployment directory..."
MSG['deploy_dir_zh']="创建部署目录..."
MSG['copying_files']="Copying application files..."
MSG['copying_files_zh']="复制应用文件..."
MSG['configuring_env']="Configuring environment variables..."
MSG['configuring_env_zh']="配置环境变量..."
MSG['starting_services']="Starting Docker services..."
MSG['starting_services_zh']="启动 Docker 服务..."
MSG['verifying_deploy']="Verifying deployment..."
MSG['verifying_deploy_zh']="验证部署状态..."
MSG['deploy_complete']="Deployment complete!"
MSG['deploy_complete_zh']="部署完成！"

# Root check
MSG['check_root']="Checking root privileges..."
MSG['check_root_zh']="检查 root 权限..."
MSG['root_required']="Root privileges required"
MSG['root_required_zh']="需要 root 权限"
MSG['root_solution']="Solution: sudo $0"
MSG['root_solution_zh']="解决方法: sudo $0"

# Docker check
MSG['docker_not_found']="Docker not installed"
MSG['docker_not_found_zh']="Docker 未安装"
MSG['docker_install_cmd']="Install Docker: curl -fsSL https://get.docker.com | sh"
MSG['docker_install_cmd_zh']="安装 Docker: curl -fsSL https://get.docker.com | sh"
MSG['docker_compose_installing']="Docker Compose not found, installing..."
MSG['docker_compose_installing_zh']="Docker Compose 未安装，尝试安装..."
MSG['docker_not_running']="Docker service not running"
MSG['docker_not_running_zh']="Docker 服务未运行"
MSG['docker_start_cmd']="Start Docker: systemctl start docker"
MSG['docker_start_cmd_zh']="启动 Docker: systemctl start docker"
MSG['docker_ok']="Docker environment check passed"
MSG['docker_ok_zh']="Docker 环境检查通过"

# Backup
MSG['backup_detected']="Existing deployment detected, backup recommended"
MSG['backup_detected_zh']="检测到现有部署，建议备份"
MSG['backup_prompt']="Backup existing deployment? (y/n): "
MSG['backup_prompt_zh']="是否备份现有部署? (y/n): "
MSG['backup_creating']="Backing up to $BACKUP_DIR..."
MSG['backup_creating_zh']="备份现有部署到 $BACKUP_DIR..."
MSG['backup_complete']="Backup complete"
MSG['backup_complete_zh']="备份完成"
MSG['backup_skip']="Skipping backup"
MSG['backup_skip_zh']="跳过备份"

# Directory creation
MSG['dirs_created']="Directory structure created"
MSG['dirs_created_zh']="目录结构创建完成"

# Files
MSG['files_copied']="Files copied successfully"
MSG['files_copied_zh']="文件复制完成"
MSG['default_config_created']="Creating default Oxidized config..."
MSG['default_config_created_zh']="创建默认 Oxidized 配置..."

# Environment
MSG['env_configured']="Environment variables configured"
MSG['env_configured_zh']="环境变量配置完成"
MSG['env_password_warn']="Please modify passwords in $PROJECT_DIR/.env!"
MSG['env_password_warn_zh']="请修改 $PROJECT_DIR/.env 中的密码！"

# Services
MSG['pulling_images']="Pulling Docker images..."
MSG['pulling_images_zh']="拉取 Docker 镜像..."
MSG['building_services']="Building and starting services..."
MSG['building_services_zh']="构建并启动服务..."
MSG['waiting_oxidized']="Waiting for Oxidized to be ready..."
MSG['waiting_oxidized_zh']="等待 Oxidized 服务就绪..."
MSG['service_status']="Service Status"

# Verification
MSG['oxidized_api_ok']="Oxidized API: Accessible"
MSG['oxidized_api_ok_zh']="Oxidized API: 可访问"
MSG['oxidized_api_fail']="Oxidized API: Not accessible yet, try again later"
MSG['oxidized_api_fail_zh']="Oxidized API: 暂时不可访问，请稍后重试"
MSG['node_manager_ok']="Node Manager UI: Accessible"
MSG['node_manager_ok_zh']="Node Manager UI: 可访问"
MSG['node_manager_fail']="Node Manager UI: Not accessible yet, try again later"
MSG['node_manager_fail_zh']="Node Manager UI: 暂时不可访问，请稍后重试"

# Access info
MSG['access_info']="Access Information"
MSG['access_info_zh']="访问地址"
MSG['config_location']="Config location: $PROJECT_DIR"
MSG['config_location_zh']="配置文件位置: $PROJECT_DIR"
MSG['common_commands']="Common Commands"
MSG['common_commands_zh']="常用命令"
MSG['cmd_logs']="View logs"
MSG['cmd_logs_zh']="查看日志"
MSG['cmd_restart']="Restart services"
MSG['cmd_restart_zh']="重启服务"
MSG['cmd_stop']="Stop services"
MSG['cmd_stop_zh']="停止服务"
MSG['cmd_update']="Update code"
MSG['cmd_update_zh']="更新代码"
MSG['first_login']="First Login"
MSG['first_login_zh']="首次登录"
MSG['username']="Username"
MSG['username_zh']="用户名"
MSG['password']="Password"
MSG['password_zh']="密码"
MSG['password_in_env']="Set in $PROJECT_DIR/.env"
MSG['password_in_env_zh']="在 $PROJECT_DIR/.env 中设置"
MSG['change_password_warn']="IMPORTANT: Change default passwords after first deployment!"
MSG['change_password_warn_zh']="重要: 首次部署后请立即修改默认密码！"

# Error messages
MSG['error_prefix']="ERROR"
MSG['error_prefix_zh']="错误"
MSG['warn_prefix']="WARN"
MSG['warn_prefix_zh']="警告"
MSG['info_prefix']="INFO"
MSG['info_prefix_zh']="信息"

# ==================== Translation Functions ====================

# Get message in current language
t() {
    local key="${1}"
    local lang_key="${key}_${LANG}"
    if [[ -n "${MSG[$lang_key]}" ]]; then
        echo "${MSG[$lang_key]}"
    else
        echo "${MSG[$key]}"  # Fallback to English
    fi
}

# Log functions with bilingual support
log_info() {
    local msg="$1"
    local lang_msg="$2"
    if [[ "$LANG" == "zh" ]]; then
        echo -e "${GREEN}[$(t 'info_prefix')]${NC} $lang_msg"
    else
        echo -e "${GREEN}[$(t 'info_prefix')]${NC} $msg"
    fi
}

log_warn() {
    local msg="$1"
    local lang_msg="$2"
    if [[ "$LANG" == "zh" ]]; then
        echo -e "${YELLOW}[$(t 'warn_prefix')]${NC} $lang_msg"
    else
        echo -e "${YELLOW}[$(t 'warn_prefix')]${NC} $msg"
    fi
}

log_error() {
    local msg="$1"
    local lang_msg="$2"
    if [[ "$LANG" == "zh" ]]; then
        echo -e "${RED}[$(t 'error_prefix')]${NC} $lang_msg"
    else
        echo -e "${RED}[$(t 'error_prefix')]${NC} $msg"
    fi
}

# ==================== Root Check ====================

check_root() {
    log_info "$(t 'check_root')" "$(t 'check_root_zh')"

    if [[ $EUID -ne 0 ]]; then
        log_error "$(t 'root_required')" "$(t 'root_required_zh')"
        log_info "$(t 'root_solution')" "$(t 'root_solution_zh')"
        exit 1
    fi
}

# ==================== Docker Check ====================

check_docker() {
    log_info "$(t 'checking_env')" "$(t 'checking_env_zh')"

    if ! command -v docker &> /dev/null; then
        log_error "$(t 'docker_not_found')" "$(t 'docker_not_found_zh')"
        log_info "$(t 'docker_install_cmd')" "$(t 'docker_install_cmd_zh')"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_warn "$(t 'docker_compose_installing')" "$(t 'docker_compose_installing_zh')"
        apt-get update && apt-get install -y docker-compose
    fi

    if ! docker info &> /dev/null; then
        log_error "$(t 'docker_not_running')" "$(t 'docker_not_running_zh')"
        log_info "$(t 'docker_start_cmd')" "$(t 'docker_start_cmd_zh')"
        exit 1
    fi

    log_info "$(t 'docker_ok')" "$(t 'docker_ok_zh')"
}

# ==================== Backup ====================

backup_existing() {
    if [[ -d "$PROJECT_DIR" ]]; then
        log_warn "$(t 'backup_detected')" "$(t 'backup_detected_zh')"

        # Non-interactive mode if not a TTY
        if [[ ! -t 0 ]]; then
            REPLY="y"
        else
            if [[ "$LANG" == "zh" ]]; then
                read -p "$(t 'backup_prompt_zh')" -n 1 -r
            else
                read -p "$(t 'backup_prompt')" -n 1 -r
            fi
            echo
        fi

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "$(t 'backup_creating')" "$(t 'backup_creating_zh')"
            mkdir -p "$BACKUP_DIR"
            cp -r "$PROJECT_DIR" "$BACKUP_DIR/$(date +%Y%m%d_%H%M%S)_backup"
            log_info "$(t 'backup_complete')" "$(t 'backup_complete_zh')"
        else
            log_info "$(t 'backup_skip')" "$(t 'backup_skip_zh')"
        fi
    fi
}

# ==================== Directory Creation ====================

create_dirs() {
    log_info "$(t 'deploy_dir')" "$(t 'deploy_dir_zh')"
    mkdir -p "$PROJECT_DIR"
    mkdir -p "$PROJECT_DIR/oxidized-config/input"
    mkdir -p "$PROJECT_DIR/oxidized-config/output"
    mkdir -p "$PROJECT_DIR/oxidized-config/model"
    mkdir -p "$BACKUP_DIR"
    log_info "$(t 'dirs_created')" "$(t 'dirs_created_zh')"
}

# ==================== File Copy ====================

copy_files() {
    log_info "$(t 'copying_files')" "$(t 'copying_files_zh')"

    # Get script directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # Copy Docker config
    cp "$SCRIPT_DIR/docker-compose-oxidized.yml" "$PROJECT_DIR/"

    # Copy Nginx config
    cp "$SCRIPT_DIR/nginx-proxy.conf" "$PROJECT_DIR/"

    # Copy node_manager app
    cp -r "$SCRIPT_DIR/node_manager" "$PROJECT_DIR/"

    # Copy oxidized custom scripts
    if [[ -d "$SCRIPT_DIR/oxidized-config/input" ]]; then
        cp -r "$SCRIPT_DIR/oxidized-config/input" "$PROJECT_DIR/oxidized-config/"
    fi
    if [[ -d "$SCRIPT_DIR/oxidized-config/model" ]]; then
        cp -r "$SCRIPT_DIR/oxidized-config/model" "$PROJECT_DIR/oxidized-config/"
    fi

    # Copy initial config (will be overwritten if exists)
    if [[ -f "$SCRIPT_DIR/oxidized-config/config" ]]; then
        cp "$SCRIPT_DIR/oxidized-config/config" "$PROJECT_DIR/oxidized-config/"
    fi

    if [[ -f "$SCRIPT_DIR/oxidized-config/credentials.json" ]]; then
        cp "$SCRIPT_DIR/oxidized-config/credentials.json" "$PROJECT_DIR/oxidized-config/"
    fi

    if [[ -f "$SCRIPT_DIR/oxidized-config/models.json" ]]; then
        cp "$SCRIPT_DIR/oxidized-config/models.json" "$PROJECT_DIR/oxidized-config/"
    fi

    # Create default config if not exists
    if [[ ! -f "$PROJECT_DIR/oxidized-config/config" ]]; then
        log_info "$(t 'default_config_created')" "$(t 'default_config_created_zh')"
        cat > "$PROJECT_DIR/oxidized-config/config" << 'EOF'
# Oxidized Main Configuration
# https://github.com/ytti/oxidized

# API Access Control
rest: 0.0.0.0:8888

# Log Configuration
log: /home/oxidized/.config/oxidized/logs/oxidized.log
log_size: 10485760
log_swapper: true

# Backup Interval (seconds) 3600 = 1 hour
interval: 3600

# Default Model Mapping
model_map:
  cisco: ios
  juniper: junos

# CSV Source Configuration
source:
  default: csv
  csv:
    file: /home/oxidized/.config/oxidized/nodes.csv
    delimiter: !ruby/regexp /,/
    map:
      name: 0
      ip: 1
      model: 2
      username: 3
      password: 4
    gpg: false

# Git Output
output:
  default: git
  git:
    single_repo: true
    user: Oxidized
    email: oxidized@localhost
    repo: /home/oxidized/.config/oxidized/output.git

# Credentials
credentials:
  default:
    username: oxidized
    password: oxidized

# Input Configuration
input:
  default: ssh, telnet
  ssh:
    secure: false
  debug: false

# Model Paths
model_dir:
  - /home/oxidized/.config/oxidized/model
  - /home/oxidized/.config/oxidized/input
EOF
    fi

    log_info "$(t 'files_copied')" "$(t 'files_copied_zh')"
}

# ==================== Environment Setup ====================

setup_env() {
    log_info "$(t 'configuring_env')" "$(t 'configuring_env_zh')"

    cat > "$PROJECT_DIR/.env" << 'EOF'
# Oxidized Authentication
OXIDIZED_USER=admin
OXIDIZED_PASSWORD=admin

# Flask Configuration
FLASK_ENV=production
EOF

    log_info "$(t 'env_configured')" "$(t 'env_configured_zh')"
    log_warn "$(t 'env_password_warn')" "$(t 'env_password_warn_zh')"
}

# ==================== Start Services ====================

start_services() {
    log_info "$(t 'starting_services')" "$(t 'starting_services_zh')"

    cd "$PROJECT_DIR"

    log_info "$(t 'pulling_images')" "$(t 'pulling_images_zh')"
    docker-compose pull

    log_info "$(t 'building_services')" "$(t 'building_services_zh')"
    docker-compose up -d

    log_info "$(t 'waiting_oxidized')" "$(t 'waiting_oxidized_zh')"
    sleep 10

    docker-compose ps

    log_info "$(t 'deploy_complete')" "$(t 'deploy_complete_zh')"
}

# ==================== Verify Deployment ====================

verify_deploy() {
    log_info "$(t 'verifying_deploy')" "$(t 'verifying_deploy_zh')"

    echo ""
    docker ps --filter "name=oxidized" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

    echo ""
    if curl -s http://localhost:8888/nodes.json > /dev/null 2>&1; then
        log_info "$(t 'oxidized_api_ok')" "$(t 'oxidized_api_ok_zh')"
    else
        log_warn "$(t 'oxidized_api_fail')" "$(t 'oxidized_api_fail_zh')"
    fi

    if curl -s http://localhost:8080/login > /dev/null 2>&1; then
        log_info "$(t 'node_manager_ok')" "$(t 'node_manager_ok_zh')"
    else
        log_warn "$(t 'node_manager_fail')" "$(t 'node_manager_fail_zh')"
    fi
}

# ==================== Print Access Info ====================

print_info() {
    local IP=$(hostname -I | awk '{print $1}')

    echo ""
    echo "=========================================="
    if [[ "$LANG" == "zh" ]]; then
        echo -e "${GREEN}部署完成！${NC}"
    else
        echo -e "${GREEN}Deployment Complete!${NC}"
    fi
    echo "=========================================="
    echo ""
    if [[ "$LANG" == "zh" ]]; then
        echo "$(t 'access_info_zh'):"
    else
        echo "$(t 'access_info'):"
    fi
    echo "  - Node Manager UI: http://${IP}:8080"
    echo "  - Oxidized API:    http://${IP}:8888"
    echo ""
    if [[ "$LANG" == "zh" ]]; then
        echo "$(t 'config_location_zh'): $PROJECT_DIR"
    else
        echo "$(t 'config_location'): $PROJECT_DIR"
    fi
    echo ""
    if [[ "$LANG" == "zh" ]]; then
        echo "$(t 'common_commands_zh'):"
        echo "  - $(t 'cmd_logs_zh'):    cd $PROJECT_DIR && docker-compose logs -f"
        echo "  - $(t 'cmd_restart_zh'):  cd $PROJECT_DIR && docker-compose restart"
        echo "  - $(t 'cmd_stop_zh'):     cd $PROJECT_DIR && docker-compose down"
        echo "  - $(t 'cmd_update_zh'):   cd $PROJECT_DIR && git pull && docker-compose up -d"
    else
        echo "$(t 'common_commands'):"
        echo "  - $(t 'cmd_logs'):    cd $PROJECT_DIR && docker-compose logs -f"
        echo "  - $(t 'cmd_restart'): cd $PROJECT_DIR && docker-compose restart"
        echo "  - $(t 'cmd_stop'):    cd $PROJECT_DIR && docker-compose down"
        echo "  - $(t 'cmd_update'):  cd $PROJECT_DIR && git pull && docker-compose up -d"
    fi
    echo ""
    if [[ "$LANG" == "zh" ]]; then
        echo "$(t 'first_login_zh'):"
        echo "  - $(t 'username_zh'): admin"
        echo "  - $(t 'password_zh'): $(t 'password_in_env_zh')"
    else
        echo "$(t 'first_login'):"
        echo "  - $(t 'username'): admin"
        echo "  - $(t 'password'): $(t 'password_in_env')"
    fi
    echo ""
    log_warn "$(t 'change_password_warn')" "$(t 'change_password_warn_zh')"
    echo ""
}

# ==================== Print Title ====================

print_title() {
    echo "=========================================="
    if [[ "$LANG" == "zh" ]]; then
        echo "  $(t 'script_title_zh')"
    else
        echo "  $(t 'script_title')"
    fi
    echo "=========================================="
    echo ""
}

# ==================== Main Function ====================

main() {
    print_title
    check_root
    check_docker
    backup_existing
    create_dirs
    copy_files
    setup_env
    start_services
    verify_deploy
    print_info
}

# Execute
main "$@"
