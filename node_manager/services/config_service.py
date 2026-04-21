"""
Config Service - Oxidized config management and versioning.
"""

import os
import hashlib
import yaml
from datetime import datetime
from typing import Dict, Any, Optional, List


OXIDIZED_CONFIG_FILE = "/oxidized_config/config"


def set_config(oxidized_config_file):
    """Set configuration from app.py."""
    global OXIDIZED_CONFIG_FILE
    OXIDIZED_CONFIG_FILE = oxidized_config_file


def _compute_hash(content: str) -> str:
    """Compute SHA-256 hash of config content."""
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def read_current_config() -> str:
    """Read current Oxidized config file."""
    try:
        if os.path.exists(OXIDIZED_CONFIG_FILE):
            with open(OXIDIZED_CONFIG_FILE, "r", encoding="utf-8") as f:
                return f.read()
        return ""
    except Exception as e:
        print(f"Error reading config: {e}")
        return ""


def parse_config(content: str) -> Dict[str, Any]:
    """Parse YAML config content."""
    try:
        import yaml

        # Custom loader that handles Ruby-specific tags
        class RubyLoader(yaml.SafeLoader):
            pass

        def ruby_regex_constructor(loader, node):
            """Handle !ruby/regexp tag by returning the regex pattern as a string."""
            return loader.construct_scalar(node)

        # Register constructor for ruby/regexp tag
        RubyLoader.add_constructor("!ruby/regexp", ruby_regex_constructor)

        return yaml.load(content, Loader=RubyLoader) or {}
    except Exception as e:
        print(f"Error parsing config: {e}")
        return {}


def write_config(content: str) -> bool:
    """Write config to Oxidized config file."""
    try:
        os.makedirs(os.path.dirname(OXIDIZED_CONFIG_FILE), exist_ok=True)
        with open(OXIDIZED_CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing config: {e}")
        return False


def validate_yaml(content: str) -> Dict[str, Any]:
    """Validate YAML content and return errors."""
    try:
        yaml.safe_load(content)
        return {"valid": True, "errors": []}
    except yaml.YAMLError as e:
        return {"valid": False, "errors": [str(e)]}


def get_menu_settings() -> Dict[str, Any]:
    """Extract menu-managed settings from current config."""
    config = parse_config(read_current_config())
    settings = {}

    # Basic settings
    settings["username"] = config.get("username", "")
    settings["password"] = config.get("password", "")
    settings["interval"] = config.get("interval", 3600)
    settings["threads"] = config.get("threads", 30)
    settings["timeout"] = config.get("timeout", 300)
    settings["debug"] = config.get("input", {}).get("debug", False) if isinstance(config.get("input"), dict) else False

    # SSH settings
    ssh = config.get("ssh", {}) or {}
    if isinstance(ssh, dict):
        settings["ssh_kex"] = ssh.get("kex", "")
        settings["ssh_encryption"] = ssh.get("encryption", "")
        settings["ssh_hmac"] = ssh.get("hmac", "")
        settings["ssh_host_key"] = ssh.get("host_key", "")
        settings["ssh_secure"] = ssh.get("secure", False)
    settings["input_default"] = config.get("input", {}).get("default", "ssh") if isinstance(config.get("input"), dict) else "ssh"

    # Output settings
    output = config.get("output", {}) or {}
    if isinstance(output, dict):
        settings["output_default"] = output.get("default", "git")
    git = config.get("git", {}) or {}
    if isinstance(git, dict):
        settings["git_user"] = git.get("user", "Oxidized")
        settings["git_email"] = git.get("email", "oxidized@example.com")

    # Vars settings
    vars_settings = config.get("vars", {}) or {}
    if isinstance(vars_settings, dict):
        settings["vars_ssh_kex"] = vars_settings.get("ssh_kex", "")
        settings["vars_ssh_encryption"] = vars_settings.get("ssh_encryption", "")
        settings["vars_remove_secret"] = vars_settings.get("remove_secret", False)
        settings["vars_enable"] = vars_settings.get("enable", "")
        settings["vars_ssh_no_keepalive"] = vars_settings.get("ssh_no_keepalive", False)
        settings["vars_ssh_no_exec"] = vars_settings.get("ssh_no_exec", False)
        settings["vars_metadata"] = vars_settings.get("metadata", False)

    return settings


def build_config_from_menu(settings: Dict[str, Any]) -> str:
    """Build full YAML config from menu settings."""
    config_lines = []

    # Basic settings
    if settings.get("username"):
        config_lines.append(f"username: {settings['username']}")
    if settings.get("password"):
        config_lines.append(f"password: {settings['password']}")
    if settings.get("interval"):
        config_lines.append(f"interval: {settings['interval']}")
    if settings.get("threads"):
        config_lines.append(f"threads: {settings['threads']}")
    if settings.get("timeout"):
        config_lines.append(f"timeout: {settings['timeout']}")

    # Input section
    config_lines.append("input:")
    if settings.get("debug"):
        config_lines.append("  debug: true")
    if settings.get("input_default"):
        config_lines.append(f"  default: {settings['input_default']}")

    # SSH section
    ssh_kex = settings.get("ssh_kex", "")
    ssh_enc = settings.get("ssh_encryption", "")
    ssh_hmac = settings.get("ssh_hmac", "")
    ssh_secure = settings.get("ssh_secure", False)

    if ssh_kex or ssh_enc or ssh_hmac or ssh_secure:
        config_lines.append("ssh:")
        if ssh_kex:
            config_lines.append(f"  kex: {ssh_kex}")
        if ssh_enc:
            config_lines.append(f"  encryption: {ssh_enc}")
        if ssh_hmac:
            config_lines.append(f"  hmac: {ssh_hmac}")
        if ssh_host_key := settings.get("ssh_host_key", ""):
            config_lines.append(f"  host_key: {ssh_host_key}")
        if ssh_secure:
            config_lines.append("  secure: true")

    # Output section
    config_lines.append("output:")
    if settings.get("output_default"):
        config_lines.append(f"  default: {settings['output_default']}")

    # Git section
    git_user = settings.get("git_user", "Oxidized")
    git_email = settings.get("git_email", "oxidized@example.com")
    config_lines.append("git:")
    config_lines.append(f"  user: {git_user}")
    config_lines.append(f"  email: {git_email}")
    config_lines.append("  single_repo: true")

    # Vars section
    vars_list = []
    if settings.get("vars_ssh_kex"):
        vars_list.append(f"ssh_kex: {settings['vars_ssh_kex']}")
    if settings.get("vars_ssh_encryption"):
        vars_list.append(f"ssh_encryption: {settings['vars_ssh_encryption']}")
    if settings.get("vars_remove_secret"):
        vars_list.append("remove_secret: true")
    if settings.get("vars_enable"):
        vars_list.append(f"enable: {settings['vars_enable']}")
    if settings.get("vars_ssh_no_keepalive"):
        vars_list.append("ssh_no_keepalive: true")
    if settings.get("vars_ssh_no_exec"):
        vars_list.append("ssh_no_exec: true")
    if settings.get("vars_metadata"):
        vars_list.append("metadata: true")

    if vars_list:
        config_lines.append("vars:")
        for v in vars_list:
            config_lines.append(f"  {v}")

    return "\n".join(config_lines) + "\n"
