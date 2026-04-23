"""
Config API routes - Oxidized config management.
"""

import yaml
from flask import Blueprint, request, jsonify
from routes.auth import login_required, admin_required
from services.config_service import (
    read_current_config,
    write_config,
    validate_yaml,
    get_menu_settings,
    build_config_from_menu,
    parse_config,
    _compute_hash,
)
from database import get_config_setting, set_config_setting, get_db_cursor
from routes import config_bp


@config_bp.route("/api/config", methods=["GET"])
def get_config():
    """Get current config with menu settings and full YAML."""
    try:
        current_yaml = read_current_config()
        menu_settings = get_menu_settings()
        return jsonify({
            "menu_settings": menu_settings,
            "yaml_content": current_yaml,
        })
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@config_bp.route("/api/config/menu", methods=["PUT"])
@admin_required
def save_menu_config():
    """Save menu-managed settings."""
    try:
        data = request.json
        settings = data.get("settings", {})
        commit_message = data.get("commit_message", "Update menu settings")

        # Build full YAML from settings
        new_yaml = build_config_from_menu(settings)

        # Validate before saving
        validation = validate_yaml(new_yaml)
        if not validation["valid"]:
            return jsonify({
                "success": False,
                "errors": validation["errors"]
            }), 400

        # Save current version to history
        current_content = read_current_config()
        _save_version(current_content, commit_message)

        # Write new config
        if write_config(new_yaml):
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "Failed to write config"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": "Internal server error"}), 500


@config_bp.route("/api/config/yaml", methods=["PUT"])
@admin_required
def save_yaml_config():
    """Save full YAML config."""
    try:
        data = request.json
        yaml_content = data.get("yaml_content", "")
        commit_message = data.get("commit_message", "Update YAML config")

        # Validate YAML
        validation = validate_yaml(yaml_content)
        if not validation["valid"]:
            return jsonify({
                "success": False,
                "errors": validation["errors"]
            }), 400

        # Save current version to history
        current_content = read_current_config()
        _save_version(current_content, commit_message)

        # Write new config
        if write_config(yaml_content):
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "Failed to write config"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": "Internal server error"}), 500


@config_bp.route("/api/config/versions", methods=["GET"])
def get_config_versions():
    """Get config version history."""
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        offset = (page - 1) * limit

        with get_db_cursor() as cursor:
            # Get total count
            cursor.execute("SELECT COUNT(*) FROM config_versions")
            total = cursor.fetchone()[0]

            # Get versions
            cursor.execute("""
                SELECT id, version, config_content, config_hash,
                       commit_message, created_at, created_by
                FROM config_versions
                ORDER BY version DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            rows = cursor.fetchall()

        versions = []
        for row in rows:
            versions.append({
                "id": row["id"],
                "version": row["version"],
                "config_hash": row["config_hash"],
                "commit_message": row["commit_message"],
                "created_at": row["created_at"],
                "created_by": row["created_by"],
            })

        return jsonify({
            "versions": versions,
            "total": total,
            "page": page,
            "limit": limit,
        })
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@config_bp.route("/api/config/diff", methods=["GET"])
def get_config_diff():
    """Get diff between two config versions."""
    try:
        from_version = int(request.args.get("from", 0))
        to_version = int(request.args.get("to", 0))

        if not from_version or not to_version:
            return jsonify({"error": "Missing version parameters"}), 400

        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT version, config_content, commit_message, created_at
                FROM config_versions WHERE version IN (?, ?)
                ORDER BY version
            """, (from_version, to_version))
            rows = cursor.fetchall()

        if len(rows) != 2:
            return jsonify({"error": "Versions not found"}), 404

        from_content = rows[0]["config_content"]
        to_content = rows[1]["config_content"]

        from_lines = from_content.splitlines()
        to_lines = to_content.splitlines()

        # Simple line diff
        diff_lines = []
        import difflib
        matcher = difflib.SequenceMatcher(None, from_lines, to_lines)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                for k in range(i2 - i1):
                    diff_lines.append({
                        "type": "equal",
                        "old_line": i1 + k + 1,
                        "new_line": j1 + k + 1,
                        "content": from_lines[i1 + k],
                    })
            elif tag == "replace":
                for k in range(i2 - i1):
                    diff_lines.append({
                        "type": "delete",
                        "old_line": i1 + k + 1,
                        "content": from_lines[i1 + k],
                    })
                for k in range(j2 - j1):
                    diff_lines.append({
                        "type": "insert",
                        "new_line": j1 + k + 1,
                        "content": to_lines[j1 + k],
                    })
            elif tag == "delete":
                for k in range(i2 - i1):
                    diff_lines.append({
                        "type": "delete",
                        "old_line": i1 + k + 1,
                        "content": from_lines[i1 + k],
                    })
            elif tag == "insert":
                for k in range(j2 - j1):
                    diff_lines.append({
                        "type": "insert",
                        "new_line": j1 + k + 1,
                        "content": to_lines[j1 + k],
                    })

        return jsonify({
            "from": {
                "version": rows[0]["version"],
                "commit_message": rows[0]["commit_message"],
                "created_at": rows[0]["created_at"],
            },
            "to": {
                "version": rows[1]["version"],
                "commit_message": rows[1]["commit_message"],
                "created_at": rows[1]["created_at"],
            },
            "diff_lines": diff_lines,
        })
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@config_bp.route("/api/config/rollback", methods=["POST"])
@admin_required
def rollback_config():
    """Rollback to a specific config version."""
    try:
        data = request.json
        target_version = int(data.get("version", 0))
        commit_message = data.get("commit_message", f"Rollback to version {target_version}")

        if not target_version:
            return jsonify({"success": False, "error": "Missing version"}), 400

        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT config_content FROM config_versions
                WHERE version = ?
            """, (target_version,))
            row = cursor.fetchone()

        if not row:
            return jsonify({"success": False, "error": "Version not found"}), 404

        target_content = row["config_content"]

        # Save current version first
        current_content = read_current_config()
        _save_version(current_content, "Before rollback")

        # Write target config
        if write_config(target_content):
            return jsonify({"success": True, "new_version": target_version})
        return jsonify({"success": False, "error": "Failed to write config"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": "Internal server error"}), 500


@config_bp.route("/api/config/validate", methods=["POST"])
def validate_config():
    """Validate YAML config content."""
    try:
        data = request.json
        yaml_content = data.get("yaml_content", "")
        validation = validate_yaml(yaml_content)
        return jsonify(validation)
    except Exception as e:
        return jsonify({"valid": False, "errors": ["Internal server error"]}), 500


@config_bp.route("/api/config/apply", methods=["POST"])
@admin_required
def apply_config():
    """Apply current config and optionally restart Oxidized."""
    try:
        restart = request.json.get("restart", True) if request.json else True

        if restart:
            from services.docker_service import restart_oxidized_container
            restart_oxidized_container()

        return jsonify({
            "success": True,
            "oxidized_restarted": restart,
        })
    except Exception as e:
        return jsonify({"success": False, "error": "Internal server error"}), 500


def _save_version(config_content: str, commit_message: str, created_by: str = "admin"):
    """Save a config version to history."""
    if not config_content:
        return

    config_hash = _compute_hash(config_content)

    try:
        with get_db_cursor() as cursor:
            # Get next version number
            cursor.execute("SELECT MAX(version) FROM config_versions")
            max_version = cursor.fetchone()[0] or 0
            new_version = max_version + 1

            # Insert new version
            cursor.execute("""
                INSERT INTO config_versions
                (version, config_content, config_hash, commit_message, created_by)
                VALUES (?, ?, ?, ?, ?)
            """, (new_version, config_content, config_hash, commit_message, created_by))
    except Exception as e:
        print(f"Error saving config version: {e}")


def init_config_versions():
    """Initialize config_versions table and save initial version."""
    try:
        # Check if we already have versions
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM config_versions")
            count = cursor.fetchone()[0]

        if count == 0:
            # Save current config as version 1
            current = read_current_config()
            if current:
                _save_version(current, "Initial configuration", "system")
    except Exception as e:
        print(f"Error initializing config versions: {e}")
