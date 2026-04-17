"""
Oxidized API routes - Oxidized integration endpoints.
"""

from flask import request, jsonify
from routes import oxidized_api_bp
from routes.auth import login_required
from services.oxidized_service import (
    get_oxidized_node_status,
    get_oxidized_nodes_status,
    get_oxidized_config,
    get_oxidized_version_history,
    get_oxidized_version_config,
    trigger_oxidized_backup,
    read_oxidized_interval,
    write_oxidized_interval,
    format_interval,
    get_oxidized_info,
)
from services.docker_service import restart_oxidized_container
import requests
import os

# Configuration (will be set by app.py)
OXIDIZED_API_URL = os.getenv("OXIDIZED_API_URL", "http://oxidized:8888")
OXIDIZED_CONFIG_FILE = "/oxidized_config/config"


def set_config(oxidized_url, oxidized_config_file):
    """Set configuration from app.py."""
    global OXIDIZED_API_URL, OXIDIZED_CONFIG_FILE
    OXIDIZED_API_URL = oxidized_url
    OXIDIZED_CONFIG_FILE = oxidized_config_file


@oxidized_api_bp.route("/api/oxidized/status", methods=["GET"])
def oxidized_status():
    """Get all nodes Oxidized status."""
    status = get_oxidized_nodes_status()
    return jsonify(status)


@oxidized_api_bp.route("/api/oxidized/info", methods=["GET"])
def oxidized_info():
    """Get Oxidized global config info."""
    info = get_oxidized_info()
    return jsonify(info)


@oxidized_api_bp.route("/api/oxidized/interval", methods=["GET"])
def oxidized_get_interval():
    """Get current backup interval in minutes."""
    seconds = read_oxidized_interval()
    return jsonify({"interval_seconds": seconds, "interval_minutes": seconds // 60})


@oxidized_api_bp.route("/api/oxidized/interval", methods=["PUT", "POST"])
def oxidized_set_interval():
    """Set backup interval."""
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
        # Config changes require container restart
        restart_oxidized_container()
        return jsonify(
            {"success": True, "interval_seconds": seconds, "interval_minutes": minutes}
        )

    return jsonify({"success": False, "error": "Failed to write config"}), 500


@oxidized_api_bp.route("/api/oxidized/node/<node_name>/status", methods=["GET"])
def oxidized_node_status(node_name):
    """Get single node Oxidized status."""
    status = get_oxidized_node_status(node_name)
    if status:
        return jsonify(status)
    return jsonify({"error": "Node not found in Oxidized"}), 404


@oxidized_api_bp.route("/api/oxidized/node/<node_name>/config", methods=["GET"])
def oxidized_node_config(node_name):
    """Get node current config."""
    config = get_oxidized_config(node_name)
    if config is not None:
        return jsonify({"config": config})
    return jsonify({"error": "Failed to get config"}), 404


@oxidized_api_bp.route("/api/oxidized/node/<node_name>/history", methods=["GET"])
def oxidized_node_history(node_name):
    """Get node version history."""
    history = get_oxidized_version_history(node_name)
    return jsonify(history)


@oxidized_api_bp.route(
    "/api/oxidized/node/<node_name>/history/<int:version_num>", methods=["GET"]
)
def oxidized_node_version_config(node_name, version_num):
    """Get node specific version config."""
    config = get_oxidized_version_config(node_name, version_num)
    if config is not None:
        return jsonify({"config": config})
    return jsonify({"error": "Failed to get version config"}), 404


@oxidized_api_bp.route("/api/oxidized/node/<node_name>/backup", methods=["POST"])
def oxidized_node_backup(node_name):
    """Trigger immediate backup."""
    result = trigger_oxidized_backup(node_name)
    if "error" in result:
        return jsonify({"success": False, "error": result["error"]}), 500
    return jsonify({"success": True, "result": result})


@oxidized_api_bp.route(
    "/api/oxidized/node/<node_name>/diff/<int:version1>/<int:version2>", methods=["GET"]
)
def oxidized_node_diff(node_name, version1, version2):
    """Get diff between two versions."""
    config1 = get_oxidized_version_config(node_name, version1)
    config2 = get_oxidized_version_config(node_name, version2)
    if config1 is None or config2 is None:
        return jsonify({"error": "Failed to get version configs"}), 404

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


@oxidized_api_bp.route("/api/oxidized/restart", methods=["POST"])
@login_required
def oxidized_restart():
    """Restart Oxidized container to reload config."""
    from services.docker_service import restart_oxidized_container

    success = restart_oxidized_container()
    if success:
        return jsonify({"success": True, "message": "Oxidized 容器已重启"})
    return jsonify({"success": False, "error": "重启失败，请检查容器状态"}), 500
