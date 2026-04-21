"""Models management API blueprint."""

from flask import Blueprint, request, jsonify
from flask import session as _session
from routes.auth import login_required
from models.user import User

# The model mappings and persistence helpers live in app.py. We import them lazily
# inside the view functions to avoid circular import during module import time.

models_bp = Blueprint("models", __name__)


@models_bp.route("/api/models", methods=["GET", "PUT"])
@login_required
def models_api():
    """Get or update enabled models.

    GET: return all available models with an enabled flag.
    PUT: update the list of enabled models (admin only).
    """
    if request.method == "GET":
        # Lazy import to avoid circular import during module load
        from app import ALL_MODELS, load_enabled_models, save_enabled_models  # type: ignore

        enabled = load_enabled_models()
        result = []
        for model_id, model_name in sorted(ALL_MODELS.items()):
            result.append({"id": model_id, "name": model_name, "enabled": model_id in enabled})
        return jsonify(result)

    # PUT
    # Admin only
    current_user = User.get_by_username(_session.get("username"))
    if not current_user or current_user.role != "admin":
        return jsonify({"success": False, "error": "Admin access required"}), 403

    data = request.json or {}
    enabled_models = data.get("models", [])
    if not isinstance(enabled_models, list):
        enabled_models = []

    from app import save_enabled_models  # type: ignore
    save_enabled_models(enabled_models)
    return jsonify({"success": True})


@models_bp.route("/api/models/all")
def models_all_api():
    """Get all available models (no auth required)."""
    from app import ALL_MODELS  # type: ignore
    result = []
    for model_id, model_name in sorted(ALL_MODELS.items()):
        result.append({"id": model_id, "name": model_name})
    return jsonify(result)
