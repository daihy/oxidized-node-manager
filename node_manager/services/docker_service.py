"""
Docker service - Docker container operations.
"""

import subprocess
import socket


def restart_oxidized_container():
    """Restart Oxidized container to load new config."""
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
        print("docker command not found, trying docker API...")
        return restart_oxidized_via_api()
    except Exception as e:
        print(f"Error restarting Oxidized container: {e}")
        return False


def restart_oxidized_via_api():
    """Restart Oxidized via Docker API."""
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect("/var/run/docker.sock")
        sock.sendall(
            b"POST /containers/oxidized/restart HTTP/1.1\r\nHost: localhost\r\n\r\n"
        )
        sock.close()
        return True
    except Exception as e:
        print(f"Docker API restart failed: {e}")
        return False
