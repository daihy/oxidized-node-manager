"""Credentials API blueprint - manage login credentials for devices."""

from flask import Blueprint, request, jsonify, session
from routes.auth import login_required
from models.user import User

credentials_bp = Blueprint("credentials", __name__)


def _load_credentials():
    # Lazy import to avoid circular import during blueprint registration
    from app import load_credentials
    return load_credentials()


def _save_credentials(creds):
    from app import save_credentials
    save_credentials(creds)


def _encode_password(pwd):
    from app import encode_password
    return encode_password(pwd)


def _decode_password(pwd_enc):
    from app import decode_password
    return decode_password(pwd_enc)


@credentials_bp.route("/api/credentials", methods=["GET", "POST"])
@login_required
def credentials_list():
    # GET: list credentials (decode passwords for display)
    if request.method == "GET":
        creds = _load_credentials()
        result = []
        for c in creds:
            result.append(
                {
                    "id": c["id"],
                    "label": c["label"],
                    "username": c["username"],
                    "password": _decode_password(c.get("password", "")),
                    "enable_password": _decode_password(c.get("enable_password", "")),
                    "description": c.get("description", ""),
                }
            )
        return jsonify(result)

    # POST: create new credential (admin only)
    data = request.json
    current_user = User.get_by_username(session.get("username"))
    if not current_user or current_user.role != "admin":
        return jsonify({"success": False, "error": "Admin access required"}), 403

    creds = _load_credentials()

    # Generate ID if not provided
    cred_id = data.get("id") or f"cred-{len(creds) + 1}"
    # Ensure unique ID
    if any(c["id"] == cred_id for c in creds):
        return jsonify({"success": False, "error": "Credential ID already exists"})

    creds.append(
        {
            "id": cred_id,
            "label": data.get("label", ""),
            "username": data.get("username", ""),
            "password": _encode_password(data.get("password", "")),
            "enable_password": _encode_password(data.get("enable_password", "")),
            "description": data.get("description", ""),
        }
    )
    _save_credentials(creds)
    return jsonify({"success": True, "id": cred_id})


@credentials_bp.route("/api/credentials/<cred_id>", methods=["GET", "PUT", "DELETE"])
@login_required
def credentials_detail(cred_id):
    """Get, update, or delete a credential by id"""
    creds = _load_credentials()

    if request.method == "GET":
        cred = next((c for c in creds if c["id"] == cred_id), None)
        if cred:
            return jsonify(
                {
                    "id": cred["id"],
                    "label": cred["label"],
                    "username": cred["username"],
                    "password": _decode_password(cred.get("password", "")),
                    "enable_password": _decode_password(cred.get("enable_password", "")),
                    "description": cred.get("description", ""),
                }
            )
        return jsonify({"error": "Credential not found"}), 404

    if request.method == "PUT":
        current_user = User.get_by_username(session.get("username"))
        if not current_user or current_user.role != "admin":
            return jsonify({"success": False, "error": "Admin access required"}), 403

        data = request.json
        idx = next((i for i, c in enumerate(creds) if c["id"] == cred_id), None)
        if idx is not None:
            creds[idx] = {
                "id": cred_id,
                "label": data.get("label", creds[idx]["label"]),
                "username": data.get("username", creds[idx]["username"]),
                "password": _encode_password(data.get("password", "")),
                "enable_password": _encode_password(data.get("enable_password", "")),
                "description": data.get("description", creds[idx].get("description", "")),
            }
            _save_credentials(creds)
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "Credential not found"})

    if request.method == "DELETE":
        current_user = User.get_by_username(session.get("username"))
        if not current_user or current_user.role != "admin":
            return jsonify({"success": False, "error": "Admin access required"}), 403

        creds = [c for c in creds if c["id"] != cred_id]
        _save_credentials(creds)
        return jsonify({"success": True})
