"""
Groups API routes - CRUD for device groups.
"""
from flask import Blueprint, request, jsonify, session
from routes.auth import login_required, admin_required
from models.group import Group
from models.user import User

groups_bp = Blueprint("groups", __name__)

@groups_bp.route("/api/groups", methods=["GET"])
@login_required
def get_groups():
    groups = Group.get_all()
    return jsonify({"groups": [g.to_dict() for g in groups]})

@groups_bp.route("/api/groups", methods=["POST"])
@login_required
def create_group():
    # Admin only
    current_user = User.get_by_username(session.get("username"))
    if not current_user or current_user.role != "admin":
        return jsonify({"success": False, "error": "Admin access required"}), 403

    data = request.json
    name = data.get("name", "").strip()
    description = data.get("description", "").strip()

    if not name:
        return jsonify({"success": False, "error": "Group name is required"}), 400

    try:
        group = Group(name=name, description=description)
        group.save()
        return jsonify({"success": True, "group": group.to_dict()})
    except Exception:
        return jsonify({"success": False, "error": "Internal server error"}), 500


@groups_bp.route("/api/groups/<int:group_id>", methods=["PUT"])
@login_required
def update_group(group_id):
    # Admin only
    current_user = User.get_by_username(session.get("username"))
    if not current_user or current_user.role != "admin":
        return jsonify({"success": False, "error": "Admin access required"}), 403

    data = request.json
    group = Group.get_by_id(group_id)
    if not group:
        return jsonify({"success": False, "error": "Group not found"}), 404

    if "name" in data:
        group.name = data["name"].strip()
    if "description" in data:
        group.description = data["description"].strip()

    try:
        group.save()
        return jsonify({"success": True, "group": group.to_dict()})
    except Exception:
        return jsonify({"success": False, "error": "Internal server error"}), 500

@groups_bp.route("/api/groups/<int:group_id>", methods=["DELETE"])
@login_required
def delete_group(group_id):
    # Admin only
    current_user = User.get_by_username(session.get("username"))
    if not current_user or current_user.role != "admin":
        return jsonify({"success": False, "error": "Admin access required"}), 403

    group = Group.get_by_id(group_id)
    if not group:
        return jsonify({"success": False, "error": "Group not found"}), 404
    try:
        group.delete()
        return jsonify({"success": True})
    except Exception:
        return jsonify({"success": False, "error": "Internal server error"}), 500
