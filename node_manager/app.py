from flask import (
    Flask,
    render_template_string,
    request,
    jsonify,
    session,
    redirect,
    url_for,
)
import json
import csv
import os
import base64
from datetime import datetime
import requests
from pathlib import Path
from functools import wraps

# Import new database module
from database import init_database, get_db_path, ensure_csv_synced
from models.node import Node
from models.user import User

# Import new route blueprints
from routes import nodes_bp, auth_bp, oxidized_api_bp
from routes.nodes import set_config as set_nodes_config

# auth.py no longer uses set_config (now uses User model with SQLite)
from routes.oxidized_api import set_config as set_oxidized_api_config
import services.oxidized_service as oxidized_service
import services.docker_service as docker_service

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "oxidized-node-manager-secret-key-2024")

CONFIG_FILE = os.getenv("CONFIG_FILE", "/oxidized_config/nodes.csv")
OXIDIZED_API_URL = os.getenv("OXIDIZED_API_URL", "http://oxidized:8888")
OXIDIZED_CONFIG_FILE = "/oxidized_config/config"
USERS_FILE = "/oxidized_config/users.json"
USER_STATUS_FILE = "/oxidized_config/user_status.json"
MODELS_FILE = "/oxidized_config/models.json"
CREDENTIALS_FILE = "/oxidized_config/credentials.json"

# Initialize database on module load
init_database()

# Ensure CSV is synced with database (fixes git checkout issues)
ensure_csv_synced()

# Configure new modules with app settings
set_nodes_config(OXIDIZED_API_URL, CONFIG_FILE)
# set_auth_config removed - auth now uses User model with SQLite
set_oxidized_api_config(OXIDIZED_API_URL, OXIDIZED_CONFIG_FILE)
oxidized_service.set_config(OXIDIZED_API_URL, OXIDIZED_CONFIG_FILE)

# Register blueprints (new modular routes)
# Note: Old routes are still active below. New blueprint routes prefixed with /api
app.register_blueprint(nodes_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(oxidized_api_bp)


def encode_password(pwd):
    """Base64 编码密码"""
    if not pwd:
        return ""
    return base64.b64encode(pwd.encode()).decode()


def decode_password(encoded):
    """Base64 解码密码"""
    if not encoded:
        return ""
    try:
        return base64.b64decode(encoded.encode()).decode()
    except:
        return ""


# 所有支持的 Oxidized Models
ALL_MODELS = {
    "ios": "Cisco IOS",
    "iosxe": "Cisco IOS-XE",
    "iosxr": "Cisco IOS-XR",
    "nxos": "Cisco NX-OS",
    "asa": "Cisco ASA",
    "ciscosmb": "Cisco Small Business (SF300/500)",
    "ciscosma": "Cisco SMA",
    "ciscoce": "Cisco CE",
    "junos": "Juniper JunOS",
    "vrp": "Huawei VRP",
    "huawei": "Huawei",
    "procurve": "HP ProCurve",
    "hpmsm": "HP MSM",
    "dellx": "Dell PowerConnect",
    "arista": "Arista EOS",
    "eos": "Arista EOS",
    "vyos": "VyOS",
    "routeros": "MikroTik RouterOS",
    "fortios": "FortiOS",
    "pfsense": "pfSense",
    "opnsense": "OPNsense",
    "panos": "Palo Alto PAN-OS",
    "sonicos": "SonicWALL",
    "ubiquiti": "Ubiquiti",
    "edgecos": "EdgeCOS",
    "dlink": "D-Link",
    "netgear": "Netgear",
    "linksyssrw": "Linksys SRW",
    "tplink": "TP-Link",
    "zynos": "Zynos",
    "comware": "HP Comware",
    "fastiron": "FastIron",
    "aireos": "Cisco AireOS",
    "meraki": "Cisco Meraki",
    "acos": "A10 ADC",
    "adtran": "Adtran",
    "alcatel": "Alcatel-Lucent",
    "aruba": "Aruba OS",
    "avaya": "Avaya",
    "broadcom": "Broadcom",
    "caleos": "CALEOS",
    "cumulus": "Cumulus Linux",
    "dnos": "Dell DNOS",
    "eos": "Arista EOS",
    "exec": "Generic Exec",
    "gaiaos": "Check Point Gaia",
    "hpeos": "HPE OS",
    "ingenico": "Ingenico",
    "ipos": "IPOS",
    "ironware": "Brocade IronWare",
    "keys": "Keys",
    "linuxgeneric": "Linux Generic",
    "microsens": "Microsens",
    "miranda": "Miranda",
    "mrv": "MRV",
    "netonix": "Netonix",
    "oneos": "OneOS",
    "openbsd": "OpenBSD",
    "openwrt": "OpenWrt",
    "orion": "Orion",
    "panos_api": "Palo Alto API",
    "powerconnect": "Dell PowerConnect",
    "radware": "Radware",
    "rgos": "RGOS",
    "riverbed": "Riverbed",
    "saos": "SAOS",
    "screenos": "Juniper ScreenOS",
    "slxos": "Brocade SLXOS",
    "sros": "Nokia SROS",
    "superloop": "Superloop",
    "tmos": "F5 TMOS",
    "tnos": "TNOS",
    "ubiquiti": "Ubiquiti",
    "vrp": "Huawei VRP",
    "weos": "Cumulus WEOS",
    "xos": "XOS",
    "zynoscli": "Zynos CLI",
}


def load_enabled_models():
    """加载已启用的模型列表"""
    if os.path.exists(MODELS_FILE):
        try:
            with open(MODELS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    # 默认返回常用模型
    return [
        "ios",
        "iosxe",
        "junos",
        "huawei",
        "vrp",
        "ciscosmb",
        "procurve",
        "vyos",
        "routeros",
        "fortios",
    ]


def save_enabled_models(models):
    """保存启用的模型列表"""
    os.makedirs(os.path.dirname(MODELS_FILE), exist_ok=True)
    with open(MODELS_FILE, "w", encoding="utf-8") as f:
        json.dump(models, f, indent=2)


# 默认凭证配置
DEFAULT_CREDENTIALS = [
    {
        "id": "huawei-admin",
        "label": "华为管理员",
        "username": "admin",
        "password": encode_password("Admin@123"),
        "enable_password": encode_password("Admin@123"),
        "description": "华为设备标准管理员账号",
    },
    {
        "id": "cisco-admin",
        "label": "Cisco 管理员",
        "username": "admin",
        "password": encode_password("cisco123"),
        "enable_password": encode_password("cisco123"),
        "description": "Cisco 设备标准管理员账号",
    },
]


def load_credentials():
    """加载凭证列表"""
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    # 返回默认凭证
    return DEFAULT_CREDENTIALS.copy()


def save_credentials(credentials):
    """保存凭证列表"""
    os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
    with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
        json.dump(credentials, f, indent=2)


# 默认用户配置（初始密码）
DEFAULT_USERS = {"admin": "admin123", "user": "user123"}


def load_users():
    """从配置文件加载用户"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return DEFAULT_USERS.copy()
    else:
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_USERS.copy(), f, indent=2)
        return DEFAULT_USERS.copy()


def save_users(users):
    """保存用户配置"""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def load_user_status():
    """加载用户状态（是否已修改默认密码）"""
    if os.path.exists(USER_STATUS_FILE):
        try:
            with open(USER_STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_user_status(status):
    """保存用户状态"""
    os.makedirs(os.path.dirname(USER_STATUS_FILE), exist_ok=True)
    with open(USER_STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)


def is_user_password_changed(username):
    """检查用户是否已修改密码"""
    status = load_user_status()
    return status.get(username, {}).get("password_changed", False)


def mark_password_as_changed(username):
    """标记用户已修改密码"""
    status = load_user_status()
    if username not in status:
        status[username] = {}
    status[username]["password_changed"] = True
    status[username]["changed_at"] = datetime.now().isoformat()
    save_user_status(status)


def login_required(f):
    """登录检查装饰器"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)

    return decorated_function


# 登录页面HTML
LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title id="page-title">Login - Oxidized Node Management</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .login-container {
            background: white;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 400px;
        }
        .login-container h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .login-container p {
            text-align: center;
            color: #999;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
            font-size: 14px;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .alert {
            padding: 12px 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            display: none;
        }
        .alert.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .lang-switch {
            position: absolute;
            top: 20px;
            right: 20px;
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        .lang-switch:hover {
            background: #f5f5f5;
        }
        .password-input-group {
            position: relative;
            display: flex;
            align-items: center;
        }
        .password-input-group input {
            width: 100%;
            padding: 12px;
            padding-right: 45px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .password-input-group input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .password-toggle {
            position: absolute;
            right: 12px;
            background: none;
            border: none;
            cursor: pointer;
            color: #666;
            font-size: 18px;
            padding: 5px;
            z-index: 10;
        }
        .password-toggle:hover {
            color: #333;
        }
    </style>
</head>
<body>
    <button class="lang-switch" onclick="switchLanguage()" id="langBtn">🌐 English</button>
    
    <div class="login-container">
        <h1 id="login-title">Login</h1>
        <p id="login-subtitle">Oxidized Node Management System</p>
        
        <div id="alert" class="alert"></div>
        
        <form onsubmit="handleLogin(event)">
            <div class="form-group">
                <label id="username-label">Username</label>
                <input type="text" id="username" required autofocus>
            </div>
            <div class="form-group">
                <label id="password-label">Password</label>
                <div class="password-input-group">
                    <input type="password" id="password" required>
                    <button type="button" class="password-toggle" onclick="togglePasswordVisibility('password')">👁️</button>
                </div>
            </div>
            <button type="submit" class="btn" id="login-btn">Login</button>
        </form>
    </div>

    <script>
        let currentLang = localStorage.getItem('lang') || 'en';
        
        const translations = {
            'zh': {
                'login_title': '登录',
                'login_subtitle': 'Oxidized 节点管理系统',
                'username_label': '用户名',
                'password_label': '密码',
                'login_btn': '登录',
                'login_error': '用户名或密码错误',
                'lang_switch': '🌐 English'
            },
            'en': {
                'login_title': 'Login',
                'login_subtitle': 'Oxidized Node Management System',
                'username_label': 'Username',
                'password_label': 'Password',
                'login_btn': 'Login',
                'login_error': 'Invalid username or password',
                'lang_switch': '🌐 中文'
            }
        };
        
        function t(key) {
            return translations[currentLang][key] || key;
        }
        
        function updateUI() {
            document.getElementById('login-title').textContent = t('login_title');
            document.getElementById('login-subtitle').textContent = t('login_subtitle');
            document.getElementById('username-label').textContent = t('username_label');
            document.getElementById('password-label').textContent = t('password_label');
            document.getElementById('login-btn').textContent = t('login_btn');
            document.getElementById('langBtn').textContent = t('lang_switch');
        }
        
        function switchLanguage() {
            currentLang = currentLang === 'en' ? 'zh' : 'en';
            localStorage.setItem('lang', currentLang);
            updateUI();
        }
        
        function togglePasswordVisibility(inputId) {
            const input = document.getElementById(inputId);
            const button = event.target;
            
            if (input.type === 'password') {
                input.type = 'text';
                button.textContent = '👁️‍🗨️';
            } else {
                input.type = 'password';
                button.textContent = '👁️';
            }
        }
        
        function handleLogin(e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    if (data.must_change_password) {
                        window.location.href = '/force-change-password';
                    } else {
                        window.location.href = '/dashboard';
                    }
                } else {
                    const alert = document.getElementById('alert');
                    alert.textContent = t('login_error');
                    alert.classList.add('error');
                    alert.style.display = 'block';
                }
            });
        }
        
        updateUI();
    </script>
</body>
</html>
"""

# 强制修改密码页面
FORCE_CHANGE_PASSWORD_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title id="page-title">Change Password - First Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 450px;
        }
        .container h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .container p {
            text-align: center;
            color: #999;
            margin-bottom: 30px;
            font-size: 14px;
            line-height: 1.6;
        }
        .warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
            font-size: 14px;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .alert {
            padding: 12px 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            display: none;
        }
        .alert.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .alert.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .password-input-group {
            position: relative;
            display: flex;
            align-items: center;
        }
        .password-input-group input {
            width: 100%;
            padding: 12px;
            padding-right: 45px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .password-input-group input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .password-toggle {
            position: absolute;
            right: 12px;
            background: none;
            border: none;
            cursor: pointer;
            color: #666;
            font-size: 18px;
            padding: 5px;
            z-index: 10;
        }
        .password-toggle:hover {
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 id="title">Change Password</h1>
        <p id="subtitle">This is your first login. For security reasons, you must change your password.</p>
        <div class="warning" id="warning">You cannot proceed to the system until you change your password.</div>
        
        <div id="alert" class="alert"></div>
        
        <form onsubmit="handleChangePassword(event)">
            <div class="form-group">
                <label id="label-current">Current Password</label>
                <div class="password-input-group">
                    <input type="password" id="currentPassword" required>
                    <button type="button" class="password-toggle" onclick="togglePasswordVisibility('currentPassword')">👁️</button>
                </div>
            </div>
            <div class="form-group">
                <label id="label-new">New Password</label>
                <div class="password-input-group">
                    <input type="password" id="newPassword" required>
                    <button type="button" class="password-toggle" onclick="togglePasswordVisibility('newPassword')">👁️</button>
                </div>
            </div>
            <div class="form-group">
                <label id="label-confirm">Confirm New Password</label>
                <div class="password-input-group">
                    <input type="password" id="confirmPassword" required>
                    <button type="button" class="password-toggle" onclick="togglePasswordVisibility('confirmPassword')">👁️</button>
                </div>
            </div>
            <button type="submit" class="btn" id="btn-change">Change Password</button>
        </form>
    </div>

    <script>
        let currentLang = localStorage.getItem('lang') || 'en';
        
        const translations = {
            'zh': {
                'title': '修改密码',
                'subtitle': '这是您首次登录。出于安全考虑，您必须修改密码。',
                'warning': '在修改密码之前，您无法访问系统。',
                'label_current': '当前密码',
                'label_new': '新密码',
                'label_confirm': '确认新密码',
                'btn_change': '修改密码',
                'error_mismatch': '两次输入的密码不一致',
                'error_same': '新密码不能与当前密码相同',
                'error_current': '当前密码错误',
                'error_short': '密码长度至少为6位',
                'success': '密码修改成功，正在跳转...',
                'lang_switch': '🌐 English'
            },
            'en': {
                'title': 'Change Password',
                'subtitle': 'This is your first login. For security reasons, you must change your password.',
                'warning': 'You cannot proceed to the system until you change your password.',
                'label_current': 'Current Password',
                'label_new': 'New Password',
                'label_confirm': 'Confirm New Password',
                'btn_change': 'Change Password',
                'error_mismatch': 'Passwords do not match',
                'error_same': 'New password cannot be the same as current password',
                'error_current': 'Current password is incorrect',
                'error_short': 'Password must be at least 6 characters',
                'success': 'Password changed successfully, redirecting...',
                'lang_switch': '🌐 中文'
            }
        };
        
        function t(key) {
            return translations[currentLang][key] || key;
        }
        
        function updateUI() {
            document.getElementById('title').textContent = t('title');
            document.getElementById('subtitle').textContent = t('subtitle');
            document.getElementById('warning').textContent = t('warning');
            document.getElementById('label-current').textContent = t('label_current');
            document.getElementById('label-new').textContent = t('label_new');
            document.getElementById('label-confirm').textContent = t('label_confirm');
            document.getElementById('btn-change').textContent = t('btn_change');
        }
        
        function showAlert(message, type = 'error') {
            const alert = document.getElementById('alert');
            alert.textContent = message;
            alert.className = `alert ${type}`;
            alert.style.display = 'block';
        }
        
        function handleChangePassword(e) {
            e.preventDefault();
            const current = document.getElementById('currentPassword').value;
            const newPass = document.getElementById('newPassword').value;
            const confirm = document.getElementById('confirmPassword').value;
            
            if (newPass.length < 6) {
                showAlert(t('error_short'));
                return;
            }
            
            if (newPass !== confirm) {
                showAlert(t('error_mismatch'));
                return;
            }
            
            if (newPass === current) {
                showAlert(t('error_same'));
                return;
            }
            
            fetch('/api/force-change-password', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    current_password: current,
                    new_password: newPass
                })
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    showAlert(t('success'), 'success');
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1500);
                } else {
                    showAlert(data.error || t('error_current'));
                }
            });
        }
        
        updateUI();
    </script>
</body>
</html>
"""

# 主仪表板（包含用户管理）
DASHBOARD_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title id="page-title">Oxidized Node Management System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header-left h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .header-left p { color: #666; font-size: 14px; }
        .header-right {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        .user-info {
            text-align: right;
        }
        .user-info p {
            color: #666;
            font-size: 14px;
        }
        .username-btn {
            background: none;
            border: none;
            color: #007bff;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            text-decoration: underline;
        }
        .username-btn:hover { color: #0056b3; }
        .btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .btn:hover { background: #0056b3; }
        .btn-danger { background: #dc3545; }
        .btn-danger:hover { background: #c82333; }
        .lang-switch { background: #28a745; }
        .lang-switch:hover { background: #218838; }
        
        .content {
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .tabs {
            display: flex;
            border-bottom: 2px solid #eee;
            margin-bottom: 20px;
            gap: 0;
        }
        .tab {
            padding: 12px 20px;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 14px;
            color: #666;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        .tab.active {
            color: #007bff;
            border-bottom-color: #007bff;
        }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        tr:hover { background: #f9f9f9; }
        
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 500;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        .password-input-group {
            position: relative;
            display: flex;
        }
        .password-input-group input {
            flex: 1;
        }
        .password-toggle {
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            cursor: pointer;
            color: #666;
            font-size: 18px;
            padding: 5px;
        }
        .password-toggle:hover {
            color: #333;
        }
        textarea {
            height: 200px;
            font-family: monospace;
        }
        
        .btn-success { background: #28a745; }
        .btn-success:hover { background: #218838; }
        
        .alert {
            padding: 12px 15px;
            border-radius: 4px;
            margin-bottom: 15px;
            display: none;
        }
        .alert.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        
        .btn-group {
            display: flex;
            gap: 5px;
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        .modal.show { display: flex; }
        .modal-content {
            background-color: white;
            margin: auto;
            padding: 30px;
            border-radius: 8px;
            width: 90%;
            max-width: 500px;
            max-height: 90vh;
            overflow-y: auto;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .modal-header h2 {
            color: #333;
            margin: 0;
        }
        .close {
            background: none;
            border: none;
            font-size: 28px;
            cursor: pointer;
            color: #999;
        }
        .close:hover { color: #333; }
        
        @media (max-width: 768px) {
            .header { flex-direction: column; align-items: flex-start; }
            .header-right { margin-top: 15px; width: 100%; justify-content: space-between; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-left">
                <h1 id="title">Oxidized Node Management System</h1>
                <p id="subtitle">Manage and monitor network device backup configurations in real-time</p>
            </div>
            <div class="header-right">
                <div class="user-info">
                    <p id="welcome"></p>
                    <button class="username-btn" id="usernameBtn" onclick="openChangePasswordModal()"></button>
                </div>
                <button class="btn lang-switch" id="langBtn" onclick="switchLanguage()">🌐 English</button>
                <button class="btn btn-danger" onclick="logout()" id="logout-btn">Logout</button>
            </div>
        </div>
        
        <div class="content">
            <div class="tabs">
                <button class="tab active" onclick="switchTab('nodes')" id="tab-nodes">📋 Nodes</button>
                <button class="tab" onclick="switchTab('add-node')" id="tab-add-node">➕ Add Node</button>
                <button class="tab" onclick="switchTab('credentials')" id="tab-credentials">🔐 Credentials</button>
                <button class="tab" onclick="switchTab('models')" id="tab-models">🔧 Models</button>
                <button class="tab" onclick="switchTab('import')" id="tab-import">📥 Import</button>
                <button class="tab" onclick="switchTab('users')" id="tab-users">👥 Users</button>
            </div>
            
            <div id="alert" class="alert"></div>
            
            <!-- 节点列表 -->
            <div id="nodes" class="tab-content active">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <button class="btn btn-success" onclick="refreshNodes()" id="btn-refresh">🔄 Refresh</button>
                        <button class="btn" onclick="refreshOxidizedStatus()" id="btn-refresh-oxidized">🔄 Refresh Oxidized Status</button>
                        <button class="btn btn-danger" onclick="restartOxidizedContainer()" id="btn-restart-oxidized">🔄 Restart Oxidized</button>
                    </div>
                    <div style="font-size: 12px; color: #666; text-align: right;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div>
                                <div id="oxidized-info">Backup Interval: <span id="backup-interval-display">Loading...</span></div>
                                <div style="font-size: 11px; color: #999;">Global setting for all nodes</div>
                            </div>
                            <button class="btn" style="padding: 5px 10px; font-size: 12px;" onclick="openBackupIntervalModal()" title="Configure Backup Interval">⚙️</button>
                        </div>
                    </div>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th id="th-name">Node Name</th>
                            <th id="th-ip">IP Address</th>
                            <th id="th-model">Device Model</th>
                            <th id="th-protocol">Protocol</th>
                            <th id="th-port">Port</th>
                            <th id="th-oxidized-status">Backup Status</th>
                            <th id="th-oxidized-last">Last Backup</th>
                            <th id="th-action">Action</th>
                        </tr>
                    </thead>
                    <tbody id="nodesList">
                        <tr><td colspan="8" style="text-align:center;" id="loading-text">Loading...</td></tr>
                    </tbody>
                </table>
            </div>
            
            <!-- 添加节点 -->
            <div id="add-node" class="tab-content">
                <div style="max-width: 500px;">
                    <form onsubmit="addNode(event)">
                        <div class="form-group">
                            <label id="label-name">Node Name</label>
                            <input type="text" id="nodeName" required>
                        </div>
                        <div class="form-group">
                            <label id="label-ip">IP Address</label>
                            <input type="text" id="nodeIp" required>
                        </div>
                        <div class="form-group">
                            <label id="label-model">Device Model</label>
                            <select id="nodeModel" required>
                                <option value="">Select device model</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label id="label-protocol">Protocol</label>
                            <select id="nodeProtocol" required onchange="updateNodePort()">
                                <option value="ssh">SSH</option>
                                <option value="telnet">Telnet</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label id="label-port">Port</label>
                            <input type="number" id="nodePort" min="1" max="65535" required value="32410">
                        </div>
                        <div class="form-group">
                            <label id="label-credential">Credential</label>
                            <select id="nodeCredential" onchange="onCredentialChange()">
                                <option value="">Select credential</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label id="label-username">Username</label>
                            <input type="text" id="nodeUsername" placeholder="Optional (select credential above)" autocomplete="off">
                        </div>
                        <div class="form-group">
                            <label id="label-password">Password</label>
                            <div class="password-input-group">
                                <input type="password" id="nodePassword" placeholder="Optional (select credential above)" autocomplete="off">
                                <button type="button" class="password-toggle" onclick="togglePasswordVisibility('nodePassword')">👁️</button>
                            </div>
                        </div>
                        <button type="submit" class="btn btn-success" id="btn-add">Add Node</button>
                    </form>
                </div>
            </div>

            <!-- 模型管理 -->
            <div id="models" class="tab-content">
                <div style="margin-bottom: 15px;">
                    <p style="color: #666; margin-bottom: 10px;">Select device models for the "Add Node" dropdown.</p>
                    <div style="display: flex; gap: 10px; align-items: center; justify-content: space-between;">
                        <div style="display: flex; gap: 10px; align-items: center; flex-wrap: nowrap;">
                            <input type="text" id="modelSearch" placeholder="Search models..." oninput="filterModels()" style="max-width: 300px;">
                            <span style="white-space: nowrap;">
                                <button class="btn" onclick="selectAllModels()" style="margin-right: 5px;">☑️ Select All</button>
                                <button class="btn" onclick="deselectAllModels()">☐ Deselect All</button>
                            </span>
                        </div>
                        <button class="btn btn-success" onclick="saveModels()">💾 Save</button>
                    </div>
                </div>
                <div style="max-height: 400px; overflow-y: auto; border: 1px solid #ddd; border-radius: 4px;">
                    <table>
                        <thead style="position: sticky; top: 0; background: #f8f9fa; z-index: 10;">
                            <tr>
                                <th style="width: 60px;">Enable</th>
                                <th>Description</th>
                                <th>Model ID</th>
                            </tr>
                        </thead>
                        <tbody id="modelsList">
                            <tr><td colspan="3">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- 凭证管理 -->
            <div id="credentials" class="tab-content">
                <div style="margin-bottom: 15px;">
                    <p style="color: #666; margin-bottom: 10px;">Manage device credentials for quick selection when adding nodes.</p>
                    <div style="display: flex; gap: 10px; align-items: center; justify-content: space-between;">
                        <div style="display: flex; gap: 10px; align-items: center; flex-wrap: nowrap;">
                            <input type="text" id="credSearch" placeholder="Search credentials..." oninput="filterCredentials()" style="max-width: 300px;">
                            <button class="btn" onclick="openAddCredentialModal()" style="white-space: nowrap;">➕ Add Credential</button>
                        </div>
                        <button class="btn btn-success" onclick="saveCredentials()">💾 Save</button>
                    </div>
                </div>
                <div style="max-height: 400px; overflow-y: auto; border: 1px solid #ddd; border-radius: 4px;">
                    <table>
                        <thead style="position: sticky; top: 0; background: #f8f9fa; z-index: 10;">
                            <tr>
                                <th style="width: 60px;">Enable</th>
                                <th>Label</th>
                                <th>Username</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody id="credentialsList">
                            <tr><td colspan="4">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- 批量导入 -->
            <div id="import" class="tab-content">
                <div style="max-width: 600px;">
                    <p style="margin-bottom: 15px; color: #666;">
                        <span id="csv-format-label">CSV Format:</span> <code>name,ip,model,protocol,port,username,password</code><br>
                        <span id="csv-example-label">Example:</span> <code>router1,192.168.1.1,ios,ssh,32410,admin,password</code>
                    </p>
                    <form onsubmit="importNodes(event)">
                        <div class="form-group">
                            <label id="label-csv">Paste CSV Content</label>
                            <textarea id="csvContent"></textarea>
                        </div>
                        <button type="submit" class="btn btn-success" id="btn-import">Import Nodes</button>
                    </form>
                </div>
            </div>
            
            <!-- 用户管理 -->
            <div id="users" class="tab-content">
                <div style="margin-bottom: 20px;">
                    <button class="btn btn-success" onclick="openAddUserModal()" id="btn-add-user">➕ Add User</button>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th id="th-user-username">Username</th>
                            <th id="th-user-created">Created</th>
                            <th id="th-user-action">Action</th>
                        </tr>
                    </thead>
                    <tbody id="usersList">
                        <tr><td colspan="3" style="text-align:center;">Loading...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- 修改密码模态框 -->
    <div id="changePasswordModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="change-pwd-title">Change Password</h2>
                <button class="close" onclick="closeChangePasswordModal()">&times;</button>
            </div>
            <form onsubmit="handleChangePassword(event)">
                <div class="form-group">
                    <label id="change-pwd-label-current">Current Password</label>
                    <div class="password-input-group">
                        <input type="password" id="changePasswordCurrent" required>
                        <button type="button" class="password-toggle" onclick="togglePasswordVisibility('changePasswordCurrent')">👁️</button>
                    </div>
                </div>
                <div class="form-group">
                    <label id="change-pwd-label-new">New Password</label>
                    <div class="password-input-group">
                        <input type="password" id="changePasswordNew" required>
                        <button type="button" class="password-toggle" onclick="togglePasswordVisibility('changePasswordNew')">👁️</button>
                    </div>
                </div>
                <div class="form-group">
                    <label id="change-pwd-label-confirm">Confirm New Password</label>
                    <div class="password-input-group">
                        <input type="password" id="changePasswordConfirm" required>
                        <button type="button" class="password-toggle" onclick="togglePasswordVisibility('changePasswordConfirm')">👁️</button>
                    </div>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button type="submit" class="btn btn-success" id="btn-change-pwd" style="flex: 1;">Save</button>
                    <button type="button" class="btn" onclick="closeChangePasswordModal()" id="btn-cancel-pwd" style="flex: 1;">Cancel</button>
                </div>
            </form>
        </div>
    </div>

    <!-- 编辑节点模态框 -->
    <div id="editModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="edit-title">Edit Node</h2>
                <button class="close" onclick="closeEditModal()">&times;</button>
            </div>
            <form onsubmit="updateNode(event)">
                <div class="form-group">
                    <label id="edit-label-name">Node Name</label>
                    <input type="text" id="editNodeName" readonly style="background: #f5f5f5;">
                </div>
                <div class="form-group">
                    <label id="edit-label-ip">IP Address</label>
                    <input type="text" id="editNodeIp" required>
                </div>
                <div class="form-group">
                    <label id="edit-label-model">Device Model</label>
                    <select id="editNodeModel" required>
                        <option value="">Select device model</option>
                    </select>
                </div>
                <div class="form-group">
                    <label id="edit-label-protocol">Protocol</label>
                    <select id="editNodeProtocol" required onchange="updateEditNodePort()">
                        <option value="ssh">SSH</option>
                        <option value="telnet">Telnet</option>
                    </select>
                </div>
                <div class="form-group">
                    <label id="edit-label-port">Port</label>
                    <input type="number" id="editNodePort" min="1" max="65535" required>
                </div>
                <div class="form-group">
                    <label id="edit-label-credential">Credential</label>
                    <select id="editNodeCredential" onchange="onEditCredentialChange()">
                        <option value="">Select credential</option>
                    </select>
                </div>
                <div class="form-group">
                    <label id="edit-label-username">Username</label>
                    <input type="text" id="editNodeUsername">
                </div>
                <div class="form-group">
                    <label id="edit-label-password">Password</label>
                    <div class="password-input-group">
                        <input type="password" id="editNodePassword">
                        <button type="button" class="password-toggle" onclick="togglePasswordVisibility('editNodePassword')">👁️</button>
                    </div>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button type="submit" class="btn btn-success" id="btn-save" style="flex: 1;">Save</button>
                    <button type="button" class="btn" onclick="closeEditModal()" id="btn-cancel" style="flex: 1;">Cancel</button>
                </div>
            </form>
        </div>
    </div>

    <!-- 用户修改密码模态框 -->
    <div id="userChangePasswordModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="user-change-pwd-title">Change Password</h2>
                <button class="close" onclick="closeUserChangePasswordModal()">&times;</button>
            </div>
            <div id="userChangePasswordAlert" class="alert"></div>
            <form onsubmit="handleUserChangePassword(event)">
                <div class="form-group">
                    <label id="user-change-pwd-label-username">Username</label>
                    <input type="text" id="userChangePasswordUsername" readonly style="background: #f5f5f5;">
                </div>
                <div class="form-group">
                    <label id="user-change-pwd-label-new">New Password</label>
                    <div class="password-input-group">
                        <input type="password" id="userChangePasswordNew" required>
                        <button type="button" class="password-toggle" onclick="togglePasswordVisibility('userChangePasswordNew')">👁️</button>
                    </div>
                </div>
                <div class="form-group">
                    <label id="user-change-pwd-label-confirm">Confirm New Password</label>
                    <div class="password-input-group">
                        <input type="password" id="userChangePasswordConfirm" required>
                        <button type="button" class="password-toggle" onclick="togglePasswordVisibility('userChangePasswordConfirm')">👁️</button>
                    </div>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button type="submit" class="btn btn-success" id="btn-user-change-pwd" style="flex: 1;">Save</button>
                    <button type="button" class="btn" onclick="closeUserChangePasswordModal()" id="btn-cancel-user-pwd" style="flex: 1;">Cancel</button>
                </div>
            </form>
        </div>
    </div>

        <!-- 添加用户模态框 -->
    <div id="addUserModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="add-user-title">Add User</h2>
                <button class="close" onclick="closeAddUserModal()">&times;</button>
            </div>
            <form onsubmit="handleAddUser(event)">
                <div class="form-group">
                    <label id="add-user-label-name">Username</label>
                    <input type="text" id="addUserUsername" required>
                </div>
                <div class="form-group">
                    <label id="add-user-label-password">Password</label>
                    <div class="password-input-group">
                        <input type="password" id="addUserPassword" required>
                        <button type="button" class="password-toggle" onclick="togglePasswordVisibility('addUserPassword')">👁️</button>
                    </div>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button type="submit" class="btn btn-success" id="btn-add-user-confirm" style="flex: 1;">Add</button>
                    <button type="button" class="btn" onclick="closeAddUserModal()" id="btn-cancel-user" style="flex: 1;">Cancel</button>
                </div>
            </form>
        </div>
    </div>

    <!-- 添加凭证模态框 -->
    <div id="addCredentialModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="add-cred-title">Add Credential</h2>
                <button class="close" onclick="closeAddCredentialModal()">&times;</button>
            </div>
            <form onsubmit="handleAddCredential(event)">
                <div class="form-group">
                    <label id="add-cred-label-id">Credential ID</label>
                    <input type="text" id="addCredId" placeholder="e.g., huawei-admin">
                </div>
                <div class="form-group">
                    <label id="add-cred-label-name">Label</label>
                    <input type="text" id="addCredLabel" placeholder="e.g., Huawei Admin" required>
                </div>
                <div class="form-group">
                    <label id="add-cred-label-username">Username</label>
                    <input type="text" id="addCredUsername" required>
                </div>
                <div class="form-group">
                    <label id="add-cred-label-password">Password</label>
                    <div class="password-input-group">
                        <input type="password" id="addCredPassword" required>
                        <button type="button" class="password-toggle" onclick="togglePasswordVisibility('addCredPassword')">👁️</button>
                    </div>
                </div>
                <div class="form-group">
                    <label id="add-cred-label-enable">Enable Password (Optional)</label>
                    <div class="password-input-group">
                        <input type="password" id="addCredEnablePassword" placeholder="Leave empty if not needed">
                        <button type="button" class="password-toggle" onclick="togglePasswordVisibility('addCredEnablePassword')">👁️</button>
                    </div>
                </div>
                <div class="form-group">
                    <label id="add-cred-label-desc">Description</label>
                    <input type="text" id="addCredDescription" placeholder="e.g., Huawei device admin account">
                </div>
                <div style="display: flex; gap: 10px;">
                    <button type="submit" class="btn btn-success" id="btn-add-cred-confirm" style="flex: 1;">Add</button>
                    <button type="button" class="btn" onclick="closeAddCredentialModal()" id="btn-cancel-cred" style="flex: 1;">Cancel</button>
                </div>
            </form>
        </div>
    </div>

    <!-- 编辑凭证模态框 -->
    <div id="editCredentialModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="edit-cred-title">Edit Credential</h2>
                <button class="close" onclick="closeEditCredentialModal()">&times;</button>
            </div>
            <form onsubmit="handleUpdateCredential(event)">
                <input type="hidden" id="editCredId">
                <div class="form-group">
                    <label id="edit-cred-label-name">Label</label>
                    <input type="text" id="editCredLabel" required>
                </div>
                <div class="form-group">
                    <label id="edit-cred-label-username">Username</label>
                    <input type="text" id="editCredUsername" required>
                </div>
                <div class="form-group">
                    <label id="edit-cred-label-password">Password</label>
                    <div class="password-input-group">
                        <input type="password" id="editCredPassword" required>
                        <button type="button" class="password-toggle" onclick="togglePasswordVisibility('editCredPassword')">👁️</button>
                    </div>
                </div>
                <div class="form-group">
                    <label id="edit-cred-label-enable">Enable Password (Optional)</label>
                    <div class="password-input-group">
                        <input type="password" id="editCredEnablePassword" placeholder="Leave empty if not needed">
                        <button type="button" class="password-toggle" onclick="togglePasswordVisibility('editCredEnablePassword')">👁️</button>
                    </div>
                </div>
                <div class="form-group">
                    <label id="edit-cred-label-desc">Description</label>
                    <input type="text" id="editCredDescription">
                </div>
                <div style="display: flex; gap: 10px;">
                    <button type="submit" class="btn btn-success" id="btn-edit-cred-confirm" style="flex: 1;">Save</button>
                    <button type="button" class="btn" onclick="closeEditCredentialModal()" id="btn-cancel-cred-edit" style="flex: 1;">Cancel</button>
                </div>
            </form>
        </div>
    </div>

    <!-- View Config Modal -->
    <div id="viewConfigModal" class="modal">
        <div class="modal-content" style="max-width: 800px;">
            <div class="modal-header">
                <h2 id="view-config-title">View Configuration</h2>
                <button class="close" onclick="closeViewConfigModal()">&times;</button>
            </div>
            <div style="margin-bottom: 15px;">
                <span id="view-config-node-name" style="font-weight: bold;"></span>
            </div>
            <div style="background: #f5f5f5; padding: 10px; border-radius: 4px; margin-bottom: 15px;">
                <span id="view-config-status"></span>
            </div>
            <div style="max-height: 400px; overflow-y: auto;">
                <textarea id="viewConfigContent" readonly style="height: 400px; font-family: monospace; font-size: 12px;"></textarea>
            </div>
            <div style="margin-top: 15px; display: flex; gap: 10px;">
                <button class="btn" onclick="copyConfig()" id="btn-copy-config">📋 Copy Config</button>
                <button class="btn" onclick="closeViewConfigModal()" id="btn-close-config">Close</button>
            </div>
        </div>
    </div>

    <!-- Version History Modal -->
    <div id="versionHistoryModal" class="modal">
        <div class="modal-content" style="max-width: 900px;">
            <div class="modal-header">
                <h2 id="version-history-title">Version History</h2>
                <button class="close" onclick="closeVersionHistoryModal()">&times;</button>
            </div>
            <div style="margin-bottom: 15px;">
                <span id="version-history-node-name" style="font-weight: bold;"></span>
            </div>
            <div id="versionHistoryList" style="max-height: 300px; overflow-y: auto; border: 1px solid #ddd; border-radius: 4px; padding: 10px;">
                Loading...
            </div>
            <div style="margin-top: 15px;">
                <h4 id="version-detail-title">Version Details</h4>
                <div id="versionDetailContent" style="background: #f5f5f5; padding: 10px; border-radius: 4px; max-height: 300px; overflow-y: auto;">
                    Select a version to view details
                </div>
            </div>
            <div style="margin-top: 15px; display: flex; gap: 10px;">
                <button class="btn" onclick="compareVersions()" id="btn-compare-versions">Compare Selected</button>
                <button class="btn" onclick="closeVersionHistoryModal()">Close</button>
            </div>
        </div>
    </div>

    <!-- Diff Modal -->
    <div id="diffModal" class="modal">
        <div class="modal-content" style="max-width: 900px;">
            <div class="modal-header">
                <h2 id="diff-title">Compare Versions</h2>
                <button class="close" onclick="closeDiffModal()">&times;</button>
            </div>
            <div style="margin-bottom: 15px;">
                <span id="diff-node-name" style="font-weight: bold;"></span>
                <span id="diff-versions" style="margin-left: 20px;"></span>
            </div>
            <div style="max-height: 400px; overflow-y: auto; font-family: monospace; font-size: 12px; background: #f5f5f5; padding: 10px; border-radius: 4px;">
                <pre id="diffContent" style="margin: 0; white-space: pre-wrap;"></pre>
            </div>
            <div style="margin-top: 15px;">
                <div style="display: flex; gap: 5px; margin-bottom: 10px;">
                    <span style="background: #ff6b6b; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px;">- Old</span>
                    <span style="background: #51cf66; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px;">+ New</span>
                </div>
            </div>
            <div style="margin-top: 15px; display: flex; gap: 10px;">
                <button class="btn" onclick="closeDiffModal()">Close</button>
            </div>
        </div>
    </div>

    <!-- Backup Interval Settings Modal -->
    <div id="backupIntervalModal" class="modal">
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <h2 id="backup-interval-title">Backup Interval Settings</h2>
                <button class="close" onclick="closeBackupIntervalModal()">&times;</button>
            </div>
            <div style="margin-bottom: 20px;">
                <p style="color: #666; font-size: 14px;">Configure how often Oxidized backs up all network devices. The interval is global and applies to all nodes.</p>
            </div>
            <form onsubmit="saveBackupInterval(event)">
                <div class="form-group">
                    <label id="backup-interval-label">Backup Interval (minutes)</label>
                    <input type="number" id="backupIntervalMinutes" min="1" max="10080" required style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;">
                    <div style="font-size: 12px; color: #999; margin-top: 5px;">Range: 1 minute to 10080 minutes (7 days). Default: 60 minutes.</div>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 20px;">
                    <button type="submit" class="btn btn-success" id="btn-save-interval" style="flex: 1;">Save</button>
                    <button type="button" class="btn" onclick="closeBackupIntervalModal()" id="btn-cancel-interval" style="flex: 1;">Cancel</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        let currentLang = localStorage.getItem('lang') || 'en';
        
        const translations = {
            'zh': {
                'title': 'Oxidized 节点管理系统',
                'subtitle': '实时管理和监控网络设备备份配置',
                'welcome': '欢迎',
                'logout_btn': '退出登录',
                'tab_nodes': '📋 节点列表',
                'tab_add_node': '➕ 添加节点',
                'tab_models': '🔧 设备型号',
                'tab_import': '📥 批量导入',
                'tab_users': '👥 用户管理',
                'node_name': '节点名称',
                'ip_address': 'IP地址',
                'device_model': '设备型号',
                'username': '用户名',
                'password': '密码',
                'action': '操作',
                'refresh': '🔄 刷新',
                'edit': '编辑',
                'delete': '删除',
                'save': '保存',
                'cancel': '取消',
                'add_user': '➕ 添加用户',
                'change_password': '修改密码',
                'logout': '退出登录',
                'success_add_node': '节点添加成功',
                'success_delete_node': '节点删除成功',
                'success_update_node': '节点更新成功',
                'success_add_user': '用户添加成功',
                'success_delete_user': '用户删除成功',
                'success_change_password': '密码修改成功',
                'success_save_models': '型号配置保存成功',
                'error_password_mismatch': '密码不匹配',
                'error_password_same': '新密码不能与当前密码相同',
                'error_password_short': '密码长度至少为6位',
                'error_current_password': '当前密码错误',
                'error_user_exists': '用户已存在',
                'confirm_delete': '确定删除?',
                'confirm_logout': '确定要退出登录吗?',
                'loading': '加载中...',
                'no_data': '-',
                'lang_switch': '🌐 English',
                'created': '创建时间',
                'user_username': '用户名',
                'user_action': '操作',
                'protocol': '协议',
                'port': '端口',
                'ssh': 'SSH',
                'telnet': 'Telnet'
            },
            'en': {
                'title': 'Oxidized Node Management System',
                'subtitle': 'Manage and monitor network device backup configurations in real-time',
                'welcome': 'Welcome',
                'logout_btn': 'Logout',
                'tab_nodes': '📋 Nodes',
                'tab_add_node': '➕ Add Node',
                'tab_credentials': '🔐 Credentials',
                'tab_models': '🔧 Models',
                'tab_import': '📥 Import',
                'tab_users': '👥 Users',
                'node_name': 'Node Name',
                'ip_address': 'IP Address',
                'device_model': 'Device Model',
                'username': 'Username',
                'password': 'Password',
                'action': 'Action',
                'refresh': '🔄 Refresh',
                'edit': 'Edit',
                'delete': 'Delete',
                'save': 'Save',
                'cancel': 'Cancel',
                'add_user': '➕ Add User',
                'change_password': 'Change Password',
                'logout': 'Logout',
                'success_add_node': 'Node added successfully',
                'success_delete_node': 'Node deleted successfully',
                'success_update_node': 'Node updated successfully',
                'success_add_user': 'User added successfully',
                'success_delete_user': 'User deleted successfully',
                'success_change_password': 'Password changed successfully',
                'success_save_models': 'Models saved successfully',
                'error_password_mismatch': 'Passwords do not match',
                'error_password_same': 'New password cannot be the same as current password',
                'error_password_short': 'Password must be at least 6 characters',
                'error_current_password': 'Current password is incorrect',
                'error_user_exists': 'User already exists',
                'confirm_delete': 'Are you sure to delete?',
                'confirm_logout': 'Are you sure to logout?',
                'loading': 'Loading...',
                'no_data': '-',
                'lang_switch': '🌐 中文',
                'created': 'Created',
                'user_username': 'Username',
                'user_action': 'Action',
                'protocol': 'Protocol',
                'port': 'Port',
                'ssh': 'SSH',
                'telnet': 'Telnet'
            }
        };
        
        function t(key) {
            return translations[currentLang][key] || key;
        }
        
        function updateUI() {
            document.getElementById('page-title').textContent = t('title');
            document.getElementById('title').textContent = t('title');
            document.getElementById('subtitle').textContent = t('subtitle');
            document.getElementById('langBtn').textContent = t('lang_switch');
            document.getElementById('logout-btn').textContent = t('logout_btn');
            
            document.getElementById('tab-nodes').textContent = t('tab_nodes');
            document.getElementById('tab-add-node').textContent = t('tab_add_node');
            document.getElementById('tab-import').textContent = t('tab_import');
            document.getElementById('tab-users').textContent = t('tab_users');
        }
        
        function switchLanguage() {
            currentLang = currentLang === 'en' ? 'zh' : 'en';
            localStorage.setItem('lang', currentLang);
            updateUI();
            refreshNodes();
            loadUsers();
        }
        
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');

            if (tabName === 'users') {
                loadUsers();
            }
            if (tabName === 'models') {
                loadModels();
            }
            if (tabName === 'credentials') {
                loadCredentials();
            }
            if (tabName === 'add-node') {
                loadModelsToSelect('nodeModel');
                loadCredentialsToSelect('nodeCredential');
            }
        }
        
        function showAlert(message, type = 'success') {
            const alert = document.getElementById('alert');
            alert.className = `alert ${type}`;
            alert.textContent = message;
            alert.style.display = 'block';
            setTimeout(() => alert.style.display = 'none', 5000);
        }
        
        function logout() {
            if (confirm(t('logout') || 'Are you sure to logout?')) {
                window.location.href = '/api/logout';
            }
        }
        
        // 密码显示/隐藏功能
        function togglePasswordVisibility(inputId) {
            const input = document.getElementById(inputId);
            const button = event.target;
            
            if (input.type === 'password') {
                input.type = 'text';
                button.textContent = '👁️‍🗨️';
            } else {
                input.type = 'password';
                button.textContent = '👁️';
            }
        }
        
        // Protocol 变化时更新 Port
        function updateNodePort() {
            const protocol = document.getElementById('nodeProtocol').value;
            const portInput = document.getElementById('nodePort');
            portInput.value = protocol === 'ssh' ? '32410' : '23';
        }
        
        function updateEditNodePort() {
            const protocol = document.getElementById('editNodeProtocol').value;
            const portInput = document.getElementById('editNodePort');
            portInput.value = protocol === 'ssh' ? '32410' : '23';
        }

        // 选择凭证时自动填充用户名密码
        function onCredentialChange() {
            const credId = document.getElementById('nodeCredential').value;
            if (!credId) return;
            const cred = allCredentials.find(c => c.id === credId);
            if (cred) {
                document.getElementById('nodeUsername').value = cred.username;
                document.getElementById('nodePassword').value = cred.password || '';
            }
        }

        function onEditCredentialChange() {
            const credId = document.getElementById('editNodeCredential').value;
            if (!credId) return;
            const cred = allCredentials.find(c => c.id === credId);
            if (cred) {
                document.getElementById('editNodeUsername').value = cred.username;
                document.getElementById('editNodePassword').value = cred.password || '';
            }
        }

        // 节点管理函数
        let oxidizedStatus = {};

        function refreshOxidizedStatus() {
            fetch('/api/oxidized/status').then(r => r.json()).then(data => {
                oxidizedStatus = {};
                if (Array.isArray(data)) {
                    data.forEach(node => {
                        // Oxidized returns 'name' not 'node_name'
                        oxidizedStatus[node.name] = node;
                    });
                }
                refreshNodes();
            }).catch(err => {
                console.error('Failed to fetch Oxidized status:', err);
                refreshNodes();
            });
        }

        function restartOxidizedContainer() {
            if (!confirm('Restart Oxidized container? This will interrupt current backups.')) return;
            showAlert('Restarting Oxidized container...', 'info');
            fetch('/api/oxidized/restart', {method: 'POST'}).then(r => r.json()).then(data => {
                if (data.success) {
                    showAlert('Oxidized container restarted successfully');
                    setTimeout(refreshOxidizedStatus, 3000);
                } else {
                    showAlert('Failed to restart Oxidized: ' + (data.error || 'Unknown error'), 'error');
                }
            }).catch(err => {
                showAlert('Error restarting Oxidized: ' + err.message, 'error');
            });
        }

        function getOxidizedLastSync(status) {
            if (!status || !status.last || !status.last.end) return 'Never';
            // status.last.end is like "2026-04-15 16:32:34 UTC"
            try {
                return new Date(status.last.end).toLocaleString();
            } catch(e) {
                return status.last.end;
            }
        }

        function getOxidizedStatusBadge(nodeName) {
            const status = oxidizedStatus[nodeName];
            if (!status) {
                return '<span style="color: #999;">Not in Oxidized</span>';
            }
            const lastSync = getOxidizedLastSync(status);
            const statusText = status.status === 'success' ? '<span style="color: #28a745;">✓ Success</span>' :
                              status.status === 'failed' ? '<span style="color: #dc3545;">✗ Failed</span>' :
                              '<span style="color: #ffc107;">⏳ ' + (status.status || 'Unknown') + '</span>';
            return `<div>${statusText}</div><div style="font-size: 11px; color: #666;">${lastSync}</div>`;
        }

        function refreshNodes() {
            document.getElementById('nodesList').innerHTML = `<tr><td colspan="8" style="text-align:center;">${t('loading')}</td></tr>`;
            fetch('/api/nodes').then(r => r.json()).then(nodes => {
                const tbody = document.getElementById('nodesList');
                if (nodes.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;">No data</td></tr>`;
                    return;
                }
                tbody.innerHTML = nodes.map(node => `
                    <tr>
                        <td>${node.name}</td>
                        <td>${node.ip}</td>
                        <td>${node.model}</td>
                        <td>${node.protocol || t('no_data')}</td>
                        <td>${node.port || t('no_data')}</td>
                        <td>${getOxidizedStatusBadge(node.name)}</td>
                        <td>${getOxidizedLastSync(oxidizedStatus[node.name]) || '-'}</td>
                        <td>
                            <div class="btn-group" style="flex-wrap: wrap; gap: 3px;">
                                <button class="btn" style="padding:5px 8px;font-size:11px;" onclick="openEditModal('${node.name}')" title="Edit">✏️</button>
                                <button class="btn" style="padding:5px 8px;font-size:11px;" onclick="viewConfig('${node.name}')" title="View Config">📄</button>
                                <button class="btn" style="padding:5px 8px;font-size:11px;" onclick="viewVersionHistory('${node.name}')" title="Version History">📜</button>
                                <button class="btn btn-success" style="padding:5px 8px;font-size:11px;" onclick="triggerBackup('${node.name}')" title="Trigger Backup">🔄</button>
                                <button class="btn btn-danger" style="padding:5px 8px;font-size:11px;" onclick="deleteNode('${node.name}')" title="Delete">🗑️</button>
                            </div>
                        </td>
                    </tr>
                `).join('');
            });
        }

        // Oxidized Config Functions
        function viewConfig(nodeName) {
            document.getElementById('view-config-node-name').textContent = nodeName;
            document.getElementById('view-config-status').textContent = 'Loading...';
            document.getElementById('viewConfigContent').value = '';
            document.getElementById('viewConfigModal').classList.add('show');

            fetch(`/api/oxidized/node/${nodeName}/config`).then(r => r.json()).then(data => {
                if (data.config) {
                    document.getElementById('viewConfigContent').value = data.config;
                    document.getElementById('view-config-status').textContent = '✓ Config loaded';
                } else {
                    document.getElementById('view-config-status').textContent = '✗ Failed to load config';
                }
            }).catch(err => {
                document.getElementById('view-config-status').textContent = '✗ Error: ' + err.message;
            });
        }

        function closeViewConfigModal() {
            document.getElementById('viewConfigModal').classList.remove('show');
        }

        function copyConfig() {
            const config = document.getElementById('viewConfigContent').value;
            navigator.clipboard.writeText(config).then(() => {
                showAlert('Config copied to clipboard');
            }).catch(() => {
                showAlert('Failed to copy config', 'error');
            });
        }

        // Oxidized Version History Functions
        let selectedVersions = [];

        function viewVersionHistory(nodeName) {
            document.getElementById('version-history-node-name').textContent = nodeName;
            document.getElementById('versionHistoryList').innerHTML = 'Loading...';
            document.getElementById('versionDetailContent').innerHTML = 'Select a version to view details';
            selectedVersions = [];
            document.getElementById('versionHistoryModal').classList.add('show');

            fetch(`/api/oxidized/node/${nodeName}/history`).then(r => r.json()).then(data => {
                if (Array.isArray(data) && data.length > 0) {
                    document.getElementById('versionHistoryList').innerHTML = data.map((v, idx) => `
                        <div style="display: flex; align-items: center; padding: 8px; border-bottom: 1px solid #eee; gap: 10px;">
                            <input type="checkbox" class="version-checkbox" data-version="${v.num || idx + 1}" style="margin: 0;">
                            <div style="flex: 1;">
                                <div style="font-weight: bold;">Version ${v.num || idx + 1}</div>
                                <div style="font-size: 12px; color: #666;">${v.date || v.timestamp || 'Unknown date'}</div>
                            </div>
                            <button class="btn" style="padding:5px 10px;font-size:11px;" onclick="viewVersionDetail('${nodeName}', ${v.num || idx + 1})">View</button>
                        </div>
                    `).join('');
                } else {
                    document.getElementById('versionHistoryList').innerHTML = '<div style="padding: 20px; text-align: center; color: #666;">No version history found</div>';
                }
            }).catch(err => {
                document.getElementById('versionHistoryList').innerHTML = '<div style="padding: 20px; text-align: center; color: #dc3545;">Error: ' + err.message + '</div>';
            });
        }

        function viewVersionDetail(nodeName, versionNum) {
            fetch(`/api/oxidized/node/${nodeName}/history/${versionNum}`).then(r => r.json()).then(data => {
                if (data.config) {
                    document.getElementById('versionDetailContent').innerHTML = `
                        <textarea readonly style="width: 100%; height: 280px; font-family: monospace; font-size: 12px;">${data.config}</textarea>
                        <div style="margin-top: 10px;">
                            <button class="btn" onclick="copyVersionConfig(${versionNum})">📋 Copy</button>
                        </div>
                    `;
                    window.currentVersionConfig = data.config;
                } else {
                    document.getElementById('versionDetailContent').innerHTML = '<div style="color: #dc3545;">Failed to load version config</div>';
                }
            });
        }

        function copyVersionConfig(versionNum) {
            if (window.currentVersionConfig) {
                navigator.clipboard.writeText(window.currentVersionConfig).then(() => {
                    showAlert('Version config copied to clipboard');
                });
            }
        }

        function compareVersions() {
            const checkboxes = document.querySelectorAll('.version-checkbox:checked');
            const versions = Array.from(checkboxes).map(cb => cb.dataset.version);
            if (versions.length !== 2) {
                showAlert('Please select exactly 2 versions to compare', 'error');
                return;
            }
            const nodeName = document.getElementById('version-history-node-name').textContent;
            closeVersionHistoryModal();
            showDiff(nodeName, versions[0], versions[1]);
        }

        function showDiff(nodeName, version1, version2) {
            document.getElementById('diff-node-name').textContent = nodeName;
            document.getElementById('diff-versions').textContent = `v${version1} vs v${version2}`;
            document.getElementById('diffContent').textContent = 'Loading...';
            document.getElementById('diffModal').classList.add('show');

            fetch(`/api/oxidized/node/${nodeName}/diff/${version1}/${version2}`).then(r => r.json()).then(data => {
                if (data.diff && data.diff.length > 0) {
                    let diffText = '';
                    data.diff.forEach(d => {
                        diffText += `Line ${d.line}:\n`;
                        diffText += `- ${d.old}\n`;
                        diffText += `+ ${d.new}\n\n`;
                    });
                    document.getElementById('diffContent').textContent = diffText;
                } else {
                    document.getElementById('diffContent').textContent = 'No differences found between the two versions.';
                }
            }).catch(err => {
                document.getElementById('diffContent').textContent = 'Error: ' + err.message;
            });
        }

        function closeVersionHistoryModal() {
            document.getElementById('versionHistoryModal').classList.remove('show');
        }

        function closeDiffModal() {
            document.getElementById('diffModal').classList.remove('show');
        }

        // Backup Interval Modal Functions
        function openBackupIntervalModal() {
            // 获取当前 interval 并显示
            fetch('/api/oxidized/interval').then(r => r.json()).then(data => {
                document.getElementById('backupIntervalMinutes').value = data.interval_minutes;
                document.getElementById('backupIntervalModal').classList.add('show');
            }).catch(err => {
                showAlert('Failed to load current interval', 'error');
            });
        }

        function closeBackupIntervalModal() {
            document.getElementById('backupIntervalModal').classList.remove('show');
        }

        function saveBackupInterval(e) {
            e.preventDefault();
            const minutes = parseInt(document.getElementById('backupIntervalMinutes').value);

            fetch('/api/oxidized/interval', {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({minutes: minutes})
            }).then(r => r.json()).then(data => {
                if (data.success) {
                    showAlert(`Backup interval updated to ${minutes} minutes`);
                    closeBackupIntervalModal();
                    refreshOxidizedInfo();
                } else {
                    showAlert('Failed to update interval: ' + (data.error || 'Unknown error'), 'error');
                }
            }).catch(err => {
                showAlert('Failed to update interval: ' + err.message, 'error');
            });
        }

        function triggerBackup(nodeName) {
            if (!confirm(`Trigger backup for ${nodeName}?`)) return;

            showAlert(`Triggering backup for ${nodeName}...`, 'info');
            fetch(`/api/oxidized/node/${nodeName}/backup`, {method: 'POST'}).then(r => r.json()).then(data => {
                if (data.success) {
                    showAlert(`Backup triggered for ${nodeName}`);
                    setTimeout(refreshOxidizedStatus, 2000);
                } else {
                    showAlert(`Failed to trigger backup: ${data.error}`, 'error');
                }
            }).catch(err => {
                showAlert(`Error: ${err.message}`, 'error');
            });
        }

        function openEditModal(name) {
            // 先加载凭证列表和型号列表
            Promise.all([
                fetch('/api/credentials').then(r => r.json()),
                fetch('/api/models').then(r => r.json())
            ]).then(([creds, models]) => {
                allCredentials = creds;

                // 填充凭证下拉框
                const credSelect = document.getElementById('editNodeCredential');
                credSelect.innerHTML = '<option value="">Select credential</option>';
                creds.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c.id;
                    opt.textContent = `${c.label} (${c.username})`;
                    credSelect.appendChild(opt);
                });

                // 填充型号下拉框
                const modelSelect = document.getElementById('editNodeModel');
                modelSelect.innerHTML = '<option value="">Select device model</option>';
                models.filter(m => m.enabled).forEach(m => {
                    const opt = document.createElement('option');
                    opt.value = m.id;
                    opt.textContent = `${m.id} - ${m.name}`;
                    modelSelect.appendChild(opt);
                });

                // 加载节点信息
                return fetch(`/api/nodes/${name}`);
            }).then(r => r.json()).then(node => {
                document.getElementById('editNodeName').value = node.name;
                document.getElementById('editNodeIp').value = node.ip;
                document.getElementById('editNodeModel').value = node.model;
                document.getElementById('editNodeProtocol').value = node.protocol || 'ssh';
                document.getElementById('editNodePort').value = node.port || '32410';
                document.getElementById('editNodeUsername').value = node.username || '';
                document.getElementById('editNodePassword').value = node.password || '';
                document.getElementById('editModal').classList.add('show');
            });
        }
        
        function closeEditModal() {
            document.getElementById('editModal').classList.remove('show');
        }
        
        function updateNode(e) {
            e.preventDefault();
            const nodeName = document.getElementById('editNodeName').value;
            const node = {
                name: nodeName,
                ip: document.getElementById('editNodeIp').value,
                model: document.getElementById('editNodeModel').value,
                protocol: document.getElementById('editNodeProtocol').value,
                port: document.getElementById('editNodePort').value,
                username: document.getElementById('editNodeUsername').value,
                password: document.getElementById('editNodePassword').value
            };
            fetch(`/api/nodes/${nodeName}`, {method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(node)})
                .then(r => r.json()).then(data => {
                    if (data.success) {
                        showAlert(t('success_update_node'));
                        closeEditModal();
                        refreshNodes();
                    }
                });
        }
        
        function addNode(e) {
            e.preventDefault();
            const node = {
                name: document.getElementById('nodeName').value,
                ip: document.getElementById('nodeIp').value,
                model: document.getElementById('nodeModel').value,
                protocol: document.getElementById('nodeProtocol').value,
                port: document.getElementById('nodePort').value,
                username: document.getElementById('nodeUsername').value,
                password: document.getElementById('nodePassword').value
            };
            fetch('/api/nodes', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(node)})
                .then(r => r.json()).then(data => {
                    if (data.success) {
                        showAlert(t('success_add_node'));
                        e.target.reset();
                        refreshNodes();
                    }
                });
        }
        
        function deleteNode(name) {
            if (confirm(t('confirm_delete'))) {
                fetch(`/api/nodes/${name}`, {method: 'DELETE'}).then(r => r.json()).then(data => {
                    if (data.success) {
                        showAlert(t('success_delete_node'));
                        refreshNodes();
                    }
                });
            }
        }
        
        function importNodes(e) {
            e.preventDefault();
            const csv = document.getElementById('csvContent').value;
            fetch('/api/import', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({csv: csv})})
                .then(r => r.json()).then(data => {
                    if (data.success) {
                        showAlert('Successfully imported ' + data.count + ' nodes');
                        document.getElementById('csvContent').value = '';
                        refreshNodes();
                    }
                });
        }
        
        // 用户管理函数
        function loadUsers() {
            fetch('/api/users').then(r => r.json()).then(users => {
                const tbody = document.getElementById('usersList');
                if (users.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="3">No users</td></tr>`;
                    return;
                }
                tbody.innerHTML = users.map(user => `
                    <tr>
                        <td>${user.username}</td>
                        <td>${user.created || t('no_data')}</td>
                        <td>
                            <div class="btn-group">
                                <button class="btn" style="padding:5px 10px;font-size:12px;" onclick="openUserChangePasswordModal('${user.username}')">${t('change_password')}</button>
                                <button class="btn btn-danger" style="padding:5px 10px;font-size:12px;" onclick="deleteUser('${user.username}')">${t('delete')}</button>
                            </div>
                        </td>
                    </tr>
                `).join('');
            });
        }

        // 模型管理函数
        let allModels = [];

        function loadModels() {
            fetch('/api/models').then(r => r.json()).then(models => {
                allModels = models;
                const tbody = document.getElementById('modelsList');
                tbody.innerHTML = models.map(m => `
                    <tr>
                        <td><input type="checkbox" id="model-${m.id}" value="${m.id}" ${m.enabled ? 'checked' : ''}></td>
                        <td>${m.name}</td>
                        <td><strong>${m.id}</strong></td>
                    </tr>
                `).join('');
            });
        }

        function saveModels() {
            const enabled = [];
            allModels.forEach(m => {
                const checkbox = document.getElementById('model-' + m.id);
                if (checkbox && checkbox.checked) {
                    enabled.push(m.id);
                }
            });
            fetch('/api/models', {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({models: enabled})
            }).then(r => r.json()).then(data => {
                if (data.success) {
                    showAlert(t('success_save_models') || 'Models saved successfully');
                }
            });
        }

        function filterModels() {
            const searchText = document.getElementById('modelSearch').value.toLowerCase();
            const filteredModels = allModels.filter(m =>
                m.id.toLowerCase().includes(searchText) ||
                m.name.toLowerCase().includes(searchText)
            );
            const tbody = document.getElementById('modelsList');
            tbody.innerHTML = filteredModels.map(m => `
                <tr>
                    <td><input type="checkbox" id="model-${m.id}" value="${m.id}" ${m.enabled ? 'checked' : ''}></td>
                    <td>${m.name}</td>
                    <td><strong>${m.id}</strong></td>
                </tr>
            `).join('');
        }

        function selectAllModels() {
            allModels.forEach(m => {
                const checkbox = document.getElementById('model-' + m.id);
                if (checkbox) checkbox.checked = true;
            });
        }

        function deselectAllModels() {
            allModels.forEach(m => {
                const checkbox = document.getElementById('model-' + m.id);
                if (checkbox) checkbox.checked = false;
            });
        }

        // 凭证管理函数
        let allCredentials = [];

        function loadCredentials() {
            fetch('/api/credentials').then(r => r.json()).then(creds => {
                allCredentials = creds;
                renderCredentialsList(creds);
            });
        }

        function renderCredentialsList(creds) {
            const tbody = document.getElementById('credentialsList');
            tbody.innerHTML = creds.map(c => `
                <tr>
                    <td><input type="checkbox" id="cred-${c.id}" value="${c.id}" checked></td>
                    <td>${c.label}</td>
                    <td>${c.username}</td>
                    <td>${c.description || ''}</td>
                    <td>
                        <div class="btn-group">
                            <button class="btn" style="padding:5px 10px;font-size:12px;" onclick="openEditCredentialModal('${c.id}')">${t('edit')}</button>
                            <button class="btn btn-danger" style="padding:5px 10px;font-size:12px;" onclick="deleteCredential('${c.id}')">${t('delete')}</button>
                        </div>
                    </td>
                </tr>
            `).join('');
        }

        function filterCredentials() {
            const searchText = document.getElementById('credSearch').value.toLowerCase();
            const filtered = allCredentials.filter(c =>
                c.label.toLowerCase().includes(searchText) ||
                c.username.toLowerCase().includes(searchText) ||
                (c.description && c.description.toLowerCase().includes(searchText))
            );
            renderCredentialsList(filtered);
        }

        function saveCredentials() {
            const enabled = [];
            allCredentials.forEach(c => {
                const checkbox = document.getElementById('cred-' + c.id);
                if (checkbox && checkbox.checked) {
                    enabled.push(c.id);
                }
            });
            // 保存逻辑：目前只是启用/禁用，后续可扩展
            showAlert('Credentials selection saved');
        }

        function openAddCredentialModal() {
            document.getElementById('addCredId').value = '';
            document.getElementById('addCredLabel').value = '';
            document.getElementById('addCredUsername').value = '';
            document.getElementById('addCredPassword').value = '';
            document.getElementById('addCredEnablePassword').value = '';
            document.getElementById('addCredDescription').value = '';
            document.getElementById('addCredentialModal').classList.add('show');
        }

        function closeAddCredentialModal() {
            document.getElementById('addCredentialModal').classList.remove('show');
        }

        function handleAddCredential(e) {
            e.preventDefault();
            const cred = {
                id: document.getElementById('addCredId').value || '',
                label: document.getElementById('addCredLabel').value,
                username: document.getElementById('addCredUsername').value,
                password: document.getElementById('addCredPassword').value,
                enable_password: document.getElementById('addCredEnablePassword').value,
                description: document.getElementById('addCredDescription').value
            };
            fetch('/api/credentials', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(cred)
            }).then(r => r.json()).then(data => {
                if (data.success) {
                    showAlert('Credential added successfully');
                    closeAddCredentialModal();
                    loadCredentials();
                } else {
                    showAlert(data.error || 'Failed to add credential', 'error');
                }
            });
        }

        function openEditCredentialModal(id) {
            const cred = allCredentials.find(c => c.id === id);
            if (!cred) return;
            document.getElementById('editCredId').value = cred.id;
            document.getElementById('editCredLabel').value = cred.label;
            document.getElementById('editCredUsername').value = cred.username;
            document.getElementById('editCredPassword').value = cred.password || '';
            document.getElementById('editCredEnablePassword').value = cred.enable_password || '';
            document.getElementById('editCredDescription').value = cred.description || '';
            document.getElementById('editCredentialModal').classList.add('show');
        }

        function closeEditCredentialModal() {
            document.getElementById('editCredentialModal').classList.remove('show');
        }

        function handleUpdateCredential(e) {
            e.preventDefault();
            const cred_id = document.getElementById('editCredId').value;
            const cred = {
                label: document.getElementById('editCredLabel').value,
                username: document.getElementById('editCredUsername').value,
                password: document.getElementById('editCredPassword').value,
                enable_password: document.getElementById('editCredEnablePassword').value,
                description: document.getElementById('editCredDescription').value
            };
            fetch(`/api/credentials/${cred_id}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(cred)
            }).then(r => r.json()).then(data => {
                if (data.success) {
                    showAlert('Credential updated successfully');
                    closeEditCredentialModal();
                    loadCredentials();
                } else {
                    showAlert(data.error || 'Failed to update credential', 'error');
                }
            });
        }

        function deleteCredential(id) {
            if (confirm(t('confirm_delete'))) {
                fetch(`/api/credentials/${id}`, {method: 'DELETE'}).then(r => r.json()).then(data => {
                    if (data.success) {
                        showAlert('Credential deleted successfully');
                        loadCredentials();
                    } else {
                        showAlert(data.error || 'Failed to delete credential', 'error');
                    }
                });
            }
        }

        function loadCredentialsToSelect(selectId) {
            fetch('/api/credentials').then(r => r.json()).then(creds => {
                const select = document.getElementById(selectId);
                if (!select) return;
                const currentValue = select.value;
                select.innerHTML = '<option value="">Select credential</option>';
                creds.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c.id;
                    opt.textContent = `${c.label} (${c.username})`;
                    select.appendChild(opt);
                });
                if (currentValue) select.value = currentValue;
            });
        }

        function loadModelsToSelect(selectId) {
            fetch('/api/models').then(r => r.json()).then(models => {
                const select = document.getElementById(selectId);
                const currentValue = select.value;
                select.innerHTML = '<option value="">Select device model</option>';
                models.filter(m => m.enabled).forEach(m => {
                    const opt = document.createElement('option');
                    opt.value = m.id;
                    opt.textContent = `${m.id} - ${m.name}`;
                    select.appendChild(opt);
                });
                if (currentValue) select.value = currentValue;
            });
        }

        function openAddUserModal() {
            document.getElementById('addUserModal').classList.add('show');
        }
        
        function closeAddUserModal() {
            document.getElementById('addUserModal').classList.remove('show');
        }
        
        function handleAddUser(e) {
            e.preventDefault();
            const username = document.getElementById('addUserUsername').value;
            const password = document.getElementById('addUserPassword').value;
            
            if (password.length < 6) {
                showAlert(t('error_password_short'), 'error');
                return;
            }
            
            fetch('/api/users', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            }).then(r => r.json()).then(data => {
                if (data.success) {
                    showAlert(t('success_add_user'));
                    closeAddUserModal();
                    document.getElementById('addUserUsername').value = '';
                    document.getElementById('addUserPassword').value = '';
                    loadUsers();
                } else {
                    showAlert(data.error, 'error');
                }
            });
        }
        
        function deleteUser(username) {
            if (confirm(t('confirm_delete'))) {
                fetch(`/api/users/${username}`, {method: 'DELETE'}).then(r => r.json()).then(data => {
                    if (data.success) {
                        showAlert(t('success_delete_user'));
                        loadUsers();
                    }
                });
            }
        }
        
        // 用户修改密码（管理员为其他用户修改）
        function openUserChangePasswordModal(username) {
            document.getElementById('userChangePasswordUsername').value = username;
            document.getElementById('userChangePasswordNew').value = '';
            document.getElementById('userChangePasswordConfirm').value = '';
            document.getElementById('userChangePasswordAlert').style.display = 'none';
            document.getElementById('userChangePasswordModal').classList.add('show');
        }
        
        function closeUserChangePasswordModal() {
            document.getElementById('userChangePasswordModal').classList.remove('show');
        }
        
        function handleUserChangePassword(e) {
            e.preventDefault();
            const username = document.getElementById('userChangePasswordUsername').value;
            const newPass = document.getElementById('userChangePasswordNew').value;
            const confirm = document.getElementById('userChangePasswordConfirm').value;
            const alertDiv = document.getElementById('userChangePasswordAlert');
            
            if (newPass.length < 6) {
                alertDiv.className = 'alert error';
                alertDiv.textContent = t('error_password_short');
                alertDiv.style.display = 'block';
                return;
            }
            
            if (newPass !== confirm) {
                alertDiv.className = 'alert error';
                alertDiv.textContent = t('error_password_mismatch');
                alertDiv.style.display = 'block';
                return;
            }
            
            fetch('/api/users-admin-change-password', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: username, new_password: newPass})
            }).then(r => r.json()).then(data => {
                if (data.success) {
                    showAlert(t('success_change_password'));
                    closeUserChangePasswordModal();
                    loadUsers();
                } else {
                    alertDiv.className = 'alert error';
                    alertDiv.textContent = data.error || 'Failed to change password';
                    alertDiv.style.display = 'block';
                }
            });
        }
        
        // 修改密码
        function openChangePasswordModal() {
            document.getElementById('changePasswordModal').classList.add('show');
        }
        
        function closeChangePasswordModal() {
            document.getElementById('changePasswordModal').classList.remove('show');
            document.getElementById('changePasswordCurrent').value = '';
            document.getElementById('changePasswordNew').value = '';
            document.getElementById('changePasswordConfirm').value = '';
        }
        
        function handleChangePassword(e) {
            e.preventDefault();
            const current = document.getElementById('changePasswordCurrent').value;
            const newPass = document.getElementById('changePasswordNew').value;
            const confirm = document.getElementById('changePasswordConfirm').value;
            
            if (newPass.length < 6) {
                showAlert(t('error_password_short'), 'error');
                return;
            }
            
            if (newPass !== confirm) {
                showAlert(t('error_password_mismatch'), 'error');
                return;
            }
            
            if (newPass === current) {
                showAlert(t('error_password_same'), 'error');
                return;
            }
            
            fetch('/api/change-password', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({current_password: current, new_password: newPass})
            }).then(r => r.json()).then(data => {
                if (data.success) {
                    showAlert(t('success_change_password'));
                    closeChangePasswordModal();
                } else {
                    showAlert(data.error, 'error');
                }
            });
        }

        // Oxidized 全局信息（备份间隔）
        function refreshOxidizedInfo() {
            fetch('/api/oxidized/info').then(r => r.json()).then(data => {
                document.getElementById('backup-interval-display').textContent = data.interval_display;
            }).catch(err => {
                console.error('Failed to fetch Oxidized info:', err);
                document.getElementById('backup-interval-display').textContent = '1 hour';
            });
        }
        
        // 初始化
        fetch('/api/user-info').then(r => r.json()).then(data => {
            document.getElementById('usernameBtn').textContent = data.username;
        });

        updateUI();
        refreshOxidizedInfo();
        refreshOxidizedStatus();
        setInterval(refreshOxidizedStatus, 60000);
    </script>
</body>
</html>
"""


@app.route("/api/login", methods=["POST"])
def login():
    """用户登录"""
    data = request.json
    users = load_users()

    username = data.get("username")
    password = data.get("password")

    if username in users and users[username] == password:
        session["username"] = username
        must_change = not is_user_password_changed(username)
        return jsonify({"success": True, "must_change_password": must_change})
    return jsonify({"success": False})


@app.route("/api/logout")
def logout():
    """用户登出"""
    session.pop("username", None)
    return redirect(url_for("login_page"))


@app.route("/api/user-info")
@login_required
def user_info():
    """获取当前登录用户信息"""
    return jsonify({"username": session.get("username")})


@app.route("/api/change-password", methods=["POST"])
@login_required
def change_password():
    """修改当前用户密码"""
    data = request.json
    users = load_users()
    username = session.get("username")

    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if len(new_password) < 6:
        return jsonify(
            {"success": False, "error": "Password must be at least 6 characters"}
        )

    if users.get(username) != current_password:
        return jsonify({"success": False, "error": "Current password is incorrect"})

    if new_password == current_password:
        return jsonify(
            {
                "success": False,
                "error": "New password cannot be the same as current password",
            }
        )

    users[username] = new_password
    save_users(users)
    mark_password_as_changed(username)

    return jsonify({"success": True})


@app.route("/api/force-change-password", methods=["POST"])
@login_required
def force_change_password():
    """首次登录强制修改密码"""
    data = request.json
    users = load_users()
    username = session.get("username")

    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if users.get(username) != current_password:
        return jsonify({"success": False, "error": "Current password is incorrect"})

    users[username] = new_password
    save_users(users)
    mark_password_as_changed(username)

    return jsonify({"success": True})


@app.route("/api/users", methods=["GET", "POST"])
@login_required
def users_api():
    """用户列表和添加用户"""
    users = load_users()
    status = load_user_status()

    if request.method == "GET":
        user_list = []
        for username in users.keys():
            user_list.append(
                {
                    "username": username,
                    "created": status.get(username, {}).get("changed_at", "N/A"),
                }
            )
        return jsonify(user_list)

    if request.method == "POST":
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify(
                {"success": False, "error": "Username and password required"}
            )

        if username in users:
            return jsonify({"success": False, "error": "User already exists"})

        if len(password) < 6:
            return jsonify(
                {"success": False, "error": "Password must be at least 6 characters"}
            )

        users[username] = password
        save_users(users)

        return jsonify({"success": True})


@app.route("/api/models", methods=["GET", "PUT"])
@login_required
def models_api():
    """获取和保存启用的模型列表"""
    if request.method == "GET":
        enabled = load_enabled_models()
        # 返回所有模型和已启用的模型列表
        result = []
        for model_id, model_name in sorted(ALL_MODELS.items()):
            result.append(
                {"id": model_id, "name": model_name, "enabled": model_id in enabled}
            )
        return jsonify(result)

    if request.method == "PUT":
        data = request.json
        enabled_models = data.get("models", [])
        save_enabled_models(enabled_models)
        return jsonify({"success": True})


@app.route("/api/models/all")
def models_all_api():
    """获取所有可用模型（无需登录）"""
    result = []
    for model_id, model_name in sorted(ALL_MODELS.items()):
        result.append({"id": model_id, "name": model_name})
    return jsonify(result)


@app.route("/api/users/<username>", methods=["DELETE"])
@login_required
def delete_user(username):
    """删除用户"""
    current_user = session.get("username")

    # 防止删除当前登录用户
    if username == current_user:
        return jsonify({"success": False, "error": "Cannot delete your own account"})

    users = load_users()

    if username not in users:
        return jsonify({"success": False, "error": "User not found"})

    del users[username]
    save_users(users)

    return jsonify({"success": True})


@app.route("/login")
def login_page():
    """登录页面"""
    if "username" in session:
        return redirect(url_for("dashboard"))
    return render_template_string(LOGIN_PAGE)


@app.route("/force-change-password")
@login_required
def force_change_password_page():
    """首次登录强制修改密码页面"""
    username = session.get("username")
    if is_user_password_changed(username):
        return redirect(url_for("dashboard"))
    return render_template_string(FORCE_CHANGE_PASSWORD_PAGE)


@app.route("/dashboard")
@login_required
def dashboard():
    """主仪表板"""
    return render_template_string(DASHBOARD_PAGE)


@app.route("/")
def index():
    """首页重定向"""
    if "username" in session:
        username = session.get("username")
        if not is_user_password_changed(username):
            return redirect(url_for("force_change_password_page"))
        return redirect(url_for("dashboard"))
    return redirect(url_for("login_page"))


@app.route("/api/nodes", methods=["GET", "POST"])
@login_required
def nodes():
    if request.method == "GET":
        nodes = read_nodes()
        return jsonify(nodes)

    if request.method == "POST":
        data = request.json
        nodes = read_nodes()

        if any(n["name"] == data["name"] for n in nodes):
            return jsonify({"success": False, "error": "Node already exists"})

        nodes.append(data)
        write_nodes(nodes)
        reload_oxidized_nodes()
        return jsonify({"success": True})


@app.route("/api/nodes/<name>", methods=["GET", "PUT", "DELETE"])
@login_required
def node_detail(name):
    nodes = read_nodes()

    if request.method == "GET":
        node = next((n for n in nodes if n["name"] == name), None)
        if node:
            return jsonify(node)
        return jsonify({"error": "Node not found"}), 404

    if request.method == "PUT":
        data = request.json
        idx = next((i for i, n in enumerate(nodes) if n["name"] == name), None)
        if idx is not None:
            nodes[idx] = data
            write_nodes(nodes)
            reload_oxidized_nodes()
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "Node not found"})

    if request.method == "DELETE":
        # 先从 Oxidized 删除节点
        delete_oxidized_node(name)
        # 再从本地列表删除
        nodes = [n for n in nodes if n["name"] != name]
        write_nodes(nodes)
        reload_oxidized_nodes()
        return jsonify({"success": True})


@app.route("/api/import", methods=["POST"])
@login_required
def import_nodes():
    data = request.json
    csv_content = data.get("csv", "")

    try:
        lines = csv_content.strip().split("\n")
        nodes = []
        for line in lines:
            if line.strip() and not line.startswith("#"):
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 3:
                    nodes.append(
                        {
                            "name": parts[0],
                            "ip": parts[1],
                            "model": parts[2],
                            "protocol": parts[3] if len(parts) > 3 else "ssh",
                            "port": parts[4]
                            if len(parts) > 4
                            else ("32410" if parts[3] == "ssh" else "23")
                            if len(parts) > 3
                            else "32410",
                            "username": parts[5] if len(parts) > 5 else "",
                            "password": parts[6] if len(parts) > 6 else "",
                        }
                    )

        existing = read_nodes()
        existing.extend(nodes)
        write_nodes(existing)
        reload_oxidized_nodes()

        return jsonify({"success": True, "count": len(nodes)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


def read_nodes():
    """
    Read nodes from database (primary) with fallback to CSV (for migration/backup).
    Returns list of node dictionaries.
    """
    # Try to read from database first
    try:
        nodes = Node.get_all()
        if nodes:
            return [n.to_dict() for n in nodes]
    except Exception as e:
        print(f"Warning: Failed to read from database: {e}")

    # Fallback to CSV if database is empty
    if not os.path.exists(CONFIG_FILE):
        return []

    nodes = []
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row:
                nodes.append(row)
    return nodes


def write_nodes(nodes):
    """
    Write nodes to both database (primary) and CSV (for Oxidized).
    This ensures both storage backends stay in sync.
    """
    # Write to database
    try:
        # Get existing node IDs from DB
        existing_nodes = {n.name: n for n in Node.get_all()}

        for node_data in nodes:
            name = node_data.get("name", "")
            model_id = node_data.get("model", "")

            if name in existing_nodes:
                # Update existing node
                node = existing_nodes[name]
                node.ip = node_data.get("ip", "")
                node.model = model_id.lower() if model_id else ""
                node.protocol = node_data.get("protocol", "ssh")
                node.port = int(node_data.get("port", 22))
                node.username = node_data.get("username", "")
                node.password = node_data.get("password", "")
                node.save()
            else:
                # Insert new node
                node = Node(
                    name=name,
                    ip=node_data.get("ip", ""),
                    model=model_id.lower() if model_id else "",
                    protocol=node_data.get("protocol", "ssh"),
                    port=int(node_data.get("port", 22)),
                    username=node_data.get("username", ""),
                    password=node_data.get("password", ""),
                )
                node.save()

        # Delete nodes that are no longer in the list
        current_names = {n.get("name") for n in nodes}
        for existing_name, existing_node in existing_nodes.items():
            if existing_name not in current_names:
                existing_node.delete()

    except Exception as e:
        print(f"Warning: Failed to write to database: {e}")

    # Write to CSV (for Oxidized compatibility)
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["name", "ip", "model", "protocol", "port", "username", "password"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for node in nodes:
            # Oxidized CSV source expects lowercase model names (e.g., "huawei", "ciscosmb")
            # The API returns proper capitalization (e.g., "Huawei", "CiscoSMB")
            model_id = node.get("model", "")
            # Convert to lowercase for CSV storage as Oxidized expects
            model_name = model_id.lower() if model_id else ""
            writer.writerow(
                {
                    "name": node.get("name", ""),
                    "ip": node.get("ip", ""),
                    "model": model_name,
                    "protocol": node.get("protocol", ""),
                    "port": node.get("port", ""),
                    "username": node.get("username", ""),
                    "password": node.get("password", ""),
                }
            )


def migrate_csv_to_database():
    """
    Migrate nodes from CSV file to database.
    This is a one-time migration to move data from CSV to SQLite.
    Returns the number of nodes migrated.
    """
    # Check if database already has data
    existing_nodes = Node.get_all()
    if existing_nodes:
        print(f"Database already has {len(existing_nodes)} nodes, skipping migration")
        return 0

    # Read from CSV
    if not os.path.exists(CONFIG_FILE):
        print(f"CSV file {CONFIG_FILE} not found, nothing to migrate")
        return 0

    csv_nodes = []
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row:
                csv_nodes.append(row)

    if not csv_nodes:
        print("CSV file is empty, nothing to migrate")
        return 0

    # Migrate to database
    for node_data in csv_nodes:
        node = Node(
            name=node_data.get("name", ""),
            ip=node_data.get("ip", ""),
            model=node_data.get("model", "").lower(),
            protocol=node_data.get("protocol", "ssh"),
            port=int(node_data.get("port", 22)),
            username=node_data.get("username", ""),
            password=node_data.get("password", ""),
        )
        node.save()

    print(f"Migrated {len(csv_nodes)} nodes from CSV to database")
    return len(csv_nodes)


def sync_oxidized_status_to_database():
    """
    Sync backup status from Oxidized API to local database.
    This updates last_backup and last_status for all nodes.
    """
    oxidized_status = get_oxidized_nodes_status()
    if not oxidized_status or not isinstance(oxidized_status, dict):
        return

    for node_name, status_data in oxidized_status.items():
        node = Node.get_by_name(node_name)
        if node:
            # Get the latest stats
            stats = status_data.get("stats", {})
            last_sync = stats.get("last", {}).get("end")
            if last_sync:
                node.last_backup = last_sync
                node.last_status = "success"
            else:
                node.last_status = "pending"
            node.save()


def reload_oxidized_nodes():
    """触发 Oxidized 重新加载节点列表"""
    try:
        response = requests.get(f"{OXIDIZED_API_URL}/reload.json", timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Warning: Failed to reload Oxidized nodes: {e}")
        return False


# ==================== Oxidized API Integration ====================


def get_oxidized_node_status(node_name):
    """获取单个节点的 Oxidized 状态"""
    try:
        response = requests.get(f"{OXIDIZED_API_URL}/node/{node_name}.json", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error getting Oxidized status for {node_name}: {e}")
        return None


def get_oxidized_nodes_status():
    """获取所有节点的 Oxidized 状态"""
    try:
        response = requests.get(f"{OXIDIZED_API_URL}/nodes.json", timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error getting Oxidized nodes status: {e}")
        return []


def get_oxidized_config(node_name):
    """获取节点的当前配置"""
    try:
        response = requests.get(
            f"{OXIDIZED_API_URL}/node/fetch/{node_name}", timeout=10
        )
        if response.status_code == 200:
            return response.text
        return None
    except Exception as e:
        print(f"Error getting Oxidized config for {node_name}: {e}")
        return None


def get_oxidized_version_history(node_name):
    """获取节点的版本历史"""
    try:
        response = requests.get(
            f"{OXIDIZED_API_URL}/node/version.json?node_full={node_name}", timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error getting Oxidized version history for {node_name}: {e}")
        return []


def get_oxidized_version_config(node_name, version_num):
    """获取节点指定版本的配置"""
    try:
        response = requests.get(
            f"{OXIDIZED_API_URL}/node/version/{node_name}/{version_num}", timeout=10
        )
        if response.status_code == 200:
            return response.text
        return None
    except Exception as e:
        print(
            f"Error getting Oxidized version config for {node_name} v{version_num}: {e}"
        )
        return None


def trigger_oxidized_backup(node_name):
    """触发节点立即备份"""
    try:
        response = requests.get(
            f"{OXIDIZED_API_URL}/node/next/{node_name}.json", timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"Error triggering Oxidized backup for {node_name}: {e}")
        return {"error": str(e)}


def delete_oxidized_node(node_name):
    """从 Oxidized 删除节点"""
    try:
        response = requests.delete(
            f"{OXIDIZED_API_URL}/node/{node_name}.json", timeout=10
        )
        if response.status_code == 200:
            return {"success": True}
        return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"Error deleting Oxidized node {node_name}: {e}")
        return {"success": False, "error": str(e)}


def get_oxidized_info():
    """获取 Oxidized 全局配置信息"""
    interval = read_oxidized_interval()
    return {"interval": interval, "interval_display": format_interval(interval)}


def read_oxidized_interval():
    """从 Oxidized 配置文件读取 interval（秒）"""
    try:
        if os.path.exists(OXIDIZED_CONFIG_FILE):
            with open(OXIDIZED_CONFIG_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                for line in content.splitlines():
                    if line.startswith("interval:"):
                        value = line.split(":", 1)[1].strip()
                        return int(value)
        return 3600  # 默认 1 小时
    except Exception as e:
        print(f"Error reading Oxidized interval: {e}")
        return 3600


def write_oxidized_interval(seconds):
    """更新 Oxidized 配置文件的 interval"""
    try:
        if not os.path.exists(OXIDIZED_CONFIG_FILE):
            return False
        with open(OXIDIZED_CONFIG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(OXIDIZED_CONFIG_FILE, "w", encoding="utf-8") as f:
            for line in lines:
                if line.startswith("interval:"):
                    f.write(f"interval: {seconds}\n")
                else:
                    f.write(line)
        return True
    except Exception as e:
        print(f"Error writing Oxidized interval: {e}")
        return False


def format_interval(seconds):
    """格式化时间间隔为可读字符串"""
    if seconds >= 3600:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''}"
    elif seconds >= 60:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        return f"{seconds} seconds"


# ==================== Oxidized API Routes ====================


@app.route("/api/oxidized/status", methods=["GET"])
@login_required
def oxidized_status():
    """获取所有节点的 Oxidized 状态"""
    status = get_oxidized_nodes_status()
    return jsonify(status)


@app.route("/api/oxidized/info", methods=["GET"])
@login_required
def oxidized_info():
    """获取 Oxidized 全局配置信息（包含备份间隔）"""
    info = get_oxidized_info()
    return jsonify(info)


@app.route("/api/oxidized/interval", methods=["GET"])
@login_required
def oxidized_get_interval():
    """获取当前备份间隔（分钟）"""
    seconds = read_oxidized_interval()
    return jsonify({"interval_seconds": seconds, "interval_minutes": seconds // 60})


@app.route("/api/oxidized/interval", methods=["PUT", "POST"])
@login_required
def oxidized_set_interval():
    """设置备份间隔"""
    data = request.json
    minutes = data.get("minutes")

    if not minutes:
        return jsonify({"success": False, "error": "minutes is required"}), 400

    try:
        minutes = int(minutes)
        if minutes < 1 or minutes > 10080:
            return jsonify(
                {"success": False, "error": "minutes must be between 1 and 10080"}
            ), 400
    except ValueError:
        return jsonify(
            {"success": False, "error": "minutes must be a valid integer"}
        ), 400

    seconds = minutes * 60
    if write_oxidized_interval(seconds):
        # 主配置修改（如 interval）需要重启 Oxidized 容器才能生效
        restart_oxidized_container()
        return jsonify(
            {"success": True, "interval_seconds": seconds, "interval_minutes": minutes}
        )

    return jsonify({"success": False, "error": "Failed to write config"}), 500


def reload_oxidized_config():
    """触发 Oxidized 重新加载配置"""
    try:
        response = requests.get(f"{OXIDIZED_API_URL}/reload.json", timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Warning: Failed to reload Oxidized config: {e}")
        return False


def restart_oxidized_container():
    """重启 Oxidized 容器以加载新的主配置（如 interval、timeout 等）"""
    import subprocess

    try:
        result = subprocess.run(
            ["docker", "restart", "oxidized"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            print("Oxidized container restarted successfully")
            return True
        else:
            print(f"Failed to restart Oxidized: {result.stderr}")
            return False
    except FileNotFoundError:
        # docker 命令不可用，尝试使用 docker API
        print("docker command not found, trying docker API...")
        return restart_oxidized_via_api()
    except Exception as e:
        print(f"Error restarting Oxidized container: {e}")
        return False


def restart_oxidized_via_api():
    """通过 Docker API 重启 Oxidized 容器"""
    import socket

    try:
        # 尝试连接 docker socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect("/var/run/docker.sock")
        # 发送重启命令
        sock.sendall(
            b"POST /containers/oxidized/restart HTTP/1.1\r\nHost: localhost\r\n\r\n"
        )
        sock.close()
        return True
    except Exception as e:
        print(f"Docker API restart failed: {e}")
        return False


@app.route("/api/oxidized/node/<node_name>/status", methods=["GET"])
@login_required
def oxidized_node_status(node_name):
    """获取单个节点的 Oxidized 详细状态"""
    status = get_oxidized_node_status(node_name)
    if status:
        return jsonify(status)
    return jsonify({"error": "Node not found in Oxidized"}), 404


@app.route("/api/oxidized/node/<node_name>/config", methods=["GET"])
@login_required
def oxidized_node_config(node_name):
    """获取节点的当前配置"""
    config = get_oxidized_config(node_name)
    if config is not None:
        return jsonify({"config": config})
    return jsonify({"error": "Failed to get config"}), 404


@app.route("/api/oxidized/node/<node_name>/history", methods=["GET"])
@login_required
def oxidized_node_history(node_name):
    """获取节点的版本历史"""
    history = get_oxidized_version_history(node_name)
    return jsonify(history)


@app.route("/api/oxidized/node/<node_name>/history/<int:version_num>", methods=["GET"])
@login_required
def oxidized_node_version_config(node_name, version_num):
    """获取节点指定版本的配置"""
    config = get_oxidized_version_config(node_name, version_num)
    if config is not None:
        return jsonify({"config": config})
    return jsonify({"error": "Failed to get version config"}), 404


@app.route("/api/oxidized/node/<node_name>/backup", methods=["POST"])
@login_required
def oxidized_node_backup(node_name):
    """触发节点立即备份"""
    result = trigger_oxidized_backup(node_name)
    if "error" in result:
        return jsonify({"success": False, "error": result["error"]}), 500
    return jsonify({"success": True, "result": result})


@app.route(
    "/api/oxidized/node/<node_name>/diff/<int:version1>/<int:version2>", methods=["GET"]
)
@login_required
def oxidized_node_diff(node_name, version1, version2):
    """获取两个版本之间的差异"""
    config1 = get_oxidized_version_config(node_name, version1)
    config2 = get_oxidized_version_config(node_name, version2)
    if config1 is None or config2 is None:
        return jsonify({"error": "Failed to get version configs"}), 404

    # 简单的行对比
    lines1 = config1.splitlines()
    lines2 = config2.splitlines()

    diff_result = []
    max_lines = max(len(lines1), len(lines2))
    for i in range(max_lines):
        l1 = lines1[i] if i < len(lines1) else ""
        l2 = lines2[i] if i < len(lines2) else ""
        if l1 != l2:
            diff_result.append({"line": i + 1, "old": l1, "new": l2})

    return jsonify({"version1": version1, "version2": version2, "diff": diff_result})


@app.route("/api/users-admin-change-password", methods=["POST"])
@login_required
def users_admin_change_password():
    """管理员为用户修改密码"""
    data = request.json
    users = load_users()
    username = data.get("username")
    new_password = data.get("new_password")

    if not username or not new_password:
        return jsonify({"success": False, "error": "Username and password required"})

    if username not in users:
        return jsonify({"success": False, "error": "User not found"})

    if len(new_password) < 6:
        return jsonify(
            {"success": False, "error": "Password must be at least 6 characters"}
        )

    users[username] = new_password
    save_users(users)

    return jsonify({"success": True})


@app.route("/api/credentials", methods=["GET", "POST"])
@login_required
def credentials_list():
    """获取或创建凭证"""
    if request.method == "GET":
        creds = load_credentials()
        # 解码密码后返回（前端不存储明文）
        result = []
        for c in creds:
            result.append(
                {
                    "id": c["id"],
                    "label": c["label"],
                    "username": c["username"],
                    "password": decode_password(c.get("password", "")),
                    "enable_password": decode_password(c.get("enable_password", "")),
                    "description": c.get("description", ""),
                }
            )
        return jsonify(result)

    if request.method == "POST":
        data = request.json
        creds = load_credentials()

        # 生成 ID
        cred_id = data.get("id") or f"cred-{len(creds) + 1}"
        # 检查 ID 唯一性
        if any(c["id"] == cred_id for c in creds):
            return jsonify({"success": False, "error": "Credential ID already exists"})

        creds.append(
            {
                "id": cred_id,
                "label": data.get("label", ""),
                "username": data.get("username", ""),
                "password": encode_password(data.get("password", "")),
                "enable_password": encode_password(data.get("enable_password", "")),
                "description": data.get("description", ""),
            }
        )
        save_credentials(creds)
        return jsonify({"success": True, "id": cred_id})


@app.route("/api/credentials/<cred_id>", methods=["GET", "PUT", "DELETE"])
@login_required
def credentials_detail(cred_id):
    """获取、更新或删除凭证"""
    creds = load_credentials()

    if request.method == "GET":
        cred = next((c for c in creds if c["id"] == cred_id), None)
        if cred:
            return jsonify(
                {
                    "id": cred["id"],
                    "label": cred["label"],
                    "username": cred["username"],
                    "password": decode_password(cred.get("password", "")),
                    "enable_password": decode_password(cred.get("enable_password", "")),
                    "description": cred.get("description", ""),
                }
            )
        return jsonify({"error": "Credential not found"}), 404

    if request.method == "PUT":
        data = request.json
        idx = next((i for i, c in enumerate(creds) if c["id"] == cred_id), None)
        if idx is not None:
            creds[idx] = {
                "id": cred_id,
                "label": data.get("label", creds[idx]["label"]),
                "username": data.get("username", creds[idx]["username"]),
                "password": encode_password(data.get("password", "")),
                "enable_password": encode_password(data.get("enable_password", "")),
                "description": data.get(
                    "description", creds[idx].get("description", "")
                ),
            }
            save_credentials(creds)
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "Credential not found"})

    if request.method == "DELETE":
        creds = [c for c in creds if c["id"] != cred_id]
        save_credentials(creds)
        return jsonify({"success": True})


if __name__ == "__main__":
    # Run one-time migration from CSV to database on startup
    print(f"Database path: {get_db_path()}")
    print("Checking for CSV to database migration...")
    migrate_csv_to_database()
    print("Starting Oxidized Node Manager...")
    app.run(host="0.0.0.0", port=5000, debug=False)
