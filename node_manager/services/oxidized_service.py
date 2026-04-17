"""
Oxidized service - Oxidized API integration.
"""

import requests
import os


OXIDIZED_API_URL = os.getenv("OXIDIZED_API_URL", "http://oxidized:8888")
OXIDIZED_CONFIG_FILE = "/oxidized_config/config"


def set_config(oxidized_url, oxidized_config_file):
    """Set configuration from app.py."""
    global OXIDIZED_API_URL, OXIDIZED_CONFIG_FILE
    OXIDIZED_API_URL = oxidized_url
    OXIDIZED_CONFIG_FILE = oxidized_config_file


def get_oxidized_node_status(node_name):
    """Get single node Oxidized status."""
    try:
        response = requests.get(f"{OXIDIZED_API_URL}/node/{node_name}.json", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error getting Oxidized status for {node_name}: {e}")
        return None


def get_oxidized_nodes_status():
    """Get all nodes Oxidized status."""
    try:
        response = requests.get(f"{OXIDIZED_API_URL}/nodes.json", timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error getting Oxidized nodes status: {e}")
        return []


def get_oxidized_config(node_name):
    """Get node current config."""
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
    """Get node version history."""
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
    """Get node specific version config."""
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
    """Trigger immediate backup."""
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


def get_oxidized_info():
    """Get Oxidized global config info."""
    interval = read_oxidized_interval()
    return {"interval": interval, "interval_display": format_interval(interval)}


def read_oxidized_interval():
    """Read interval from Oxidized config file (in seconds)."""
    try:
        if os.path.exists(OXIDIZED_CONFIG_FILE):
            with open(OXIDIZED_CONFIG_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                for line in content.splitlines():
                    if line.startswith("interval:"):
                        value = line.split(":", 1)[1].strip()
                        return int(value)
        return 3600  # Default 1 hour
    except Exception as e:
        print(f"Error reading Oxidized interval: {e}")
        return 3600


def write_oxidized_interval(seconds):
    """Write interval to Oxidized config file."""
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
    """Format interval to human readable string."""
    if seconds >= 3600:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''}"
    elif seconds >= 60:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        return f"{seconds} seconds"


def reload_oxidized_config():
    """Trigger Oxidized to reload config."""
    try:
        response = requests.get(f"{OXIDIZED_API_URL}/reload.json", timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Warning: Failed to reload Oxidized config: {e}")
        return False
