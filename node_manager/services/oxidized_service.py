"""
Oxidized service - Oxidized API integration.
"""

import requests
import os


OXIDIZED_API_URL = os.getenv("OXIDIZED_API_URL", "http://oxidized:8888")
OXIDIZED_CONFIG_FILE = "/oxidized_config/config"
OXIDIZED_API_TOKEN = ""


def set_config(oxidized_url, oxidized_config_file, api_token=""):
    """Set configuration from app.py."""
    global OXIDIZED_API_URL, OXIDIZED_CONFIG_FILE, OXIDIZED_API_TOKEN
    OXIDIZED_API_URL = oxidized_url
    OXIDIZED_CONFIG_FILE = oxidized_config_file
    OXIDIZED_API_TOKEN = api_token


def _get_headers():
    """Build request headers with API token if configured."""
    headers = {}
    if OXIDIZED_API_TOKEN:
        headers["Api-Token"] = OXIDIZED_API_TOKEN
    return headers


def get_oxidized_node_status(node_name):
    """Get single node Oxidized status."""
    try:
        response = requests.get(
            f"{OXIDIZED_API_URL}/node/{node_name}.json",
            headers=_get_headers(),
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error getting Oxidized status for {node_name}: {e}")
        return None


def get_oxidized_nodes_status():
    """Get all nodes Oxidized status."""
    try:
        response = requests.get(
            f"{OXIDIZED_API_URL}/nodes.json",
            headers=_get_headers(),
            timeout=10
        )
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
            f"{OXIDIZED_API_URL}/node/fetch/{node_name}",
            headers=_get_headers(),
            timeout=10
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
            f"{OXIDIZED_API_URL}/node/version.json?node_full={node_name}",
            headers=_get_headers(),
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error getting Oxidized version history for {node_name}: {e}")
        return []


def get_oxidized_version_config(node_name, oid, epoch=None):
    """Get node specific version config using direct git access.

    Oxidized 0.36 with oxidized-web 0.18.1 has a bug where /node/version/view
    returns NoMethodError. We work around it by accessing the git repo directly
    via Docker API.

    Additionally, Oxidized's internal @gitcache can return stale OIDs that no
    longer exist in the git repo. When the OID doesn't exist, we fall back to
    timestamp-based lookup using the epoch parameter.
    """
    import docker
    import sys
    print(f"DEBUG: get_oxidized_version_config called with node={node_name}, oid={oid}, epoch={epoch}", flush=True)
    try:
        client = docker.from_env()
        git_dir = "/home/oxidized/.config/oxidized/git"
        container = client.containers.get("oxidized")

        # Helper to run git command and return (exit_code, output)
        def git_exec(args):
            result = container.exec_run(
                ["git", "-C", git_dir, "-c", f"safe.directory={git_dir}"] + args
            )
            return result.exit_code, result.output.decode("utf-8", errors="replace")

        # Try direct OID lookup first (works when Oxidized cache is fresh)
        for path_variant in [f"{oid}:{node_name}", f"{oid}:/{node_name}", oid]:
            ec, out = git_exec(["show", path_variant])
            if ec == 0:
                print(f"DEBUG: Found config via direct OID lookup: oid={path_variant}", flush=True)
                return out

        # OID not found - Oxidized cache is stale. Use epoch timestamp to find the commit.
        if epoch:
            print(f"DEBUG: OID {oid} not found in git, falling back to epoch {epoch}", flush=True)
            # Convert epoch (Unix timestamp seconds) to date string for git
            # Add 1 second to include commits at exactly the epoch time
            from datetime import datetime, timezone
            date_str = datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            # Use git log to find commits at or before this date that touch node_name
            ec, commit_list = git_exec(
                ["log", "--until", f"{date_str}",
                 "--format=%H",
                 "--name-only", "--", node_name]
            )
            if ec == 0 and commit_list.strip():
                lines = commit_list.strip().split("\n")
                if lines:
                    commit_hash = lines[0].strip()
                    if commit_hash:
                        print(f"DEBUG: Found commit {commit_hash} via epoch lookup for {node_name}", flush=True)
                        ec2, config = git_exec(["show", f"{commit_hash}:{node_name}"])
                        if ec2 == 0:
                            return config
                        # Try with leading slash
                        ec3, config3 = git_exec(["show", f"{commit_hash}:/{node_name}"])
                        if ec3 == 0:
                            return config3

        print(f"ERROR: Git show failed for oid={oid}, node={node_name}", flush=True)
        return None
    except Exception as e:
        import traceback
        print(f"ERROR: Exception in get_oxidized_version_config: {e}", flush=True)
        print(f"ERROR: Traceback: {traceback.format_exc()}", flush=True)
        return None


def trigger_oxidized_backup(node_name):
    """Trigger immediate backup."""
    try:
        response = requests.get(
            f"{OXIDIZED_API_URL}/node/next/{node_name}.json",
            headers=_get_headers(),
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"Error triggering Oxidized backup for {node_name}: {e}")
        return {"error": "Backup request failed"}


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
        response = requests.get(
            f"{OXIDIZED_API_URL}/reload.json",
            headers=_get_headers(),
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Warning: Failed to reload Oxidized config: {e}")
        return False
