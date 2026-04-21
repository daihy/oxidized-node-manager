"""
Page routes blueprint - UI page routes (login, dashboard, etc.)
"""

from flask import Blueprint, render_template, redirect, url_for, session
from routes.auth import login_required as auth_login_required

pages_bp = Blueprint("pages", __name__)


def is_user_password_changed(username):
    """Check if user has changed their password (from legacy user_status.json)."""
    import os
    import json
    USER_STATUS_FILE = "/oxidized_config/user_status.json"

    if os.path.exists(USER_STATUS_FILE):
        try:
            with open(USER_STATUS_FILE, "r", encoding="utf-8") as f:
                status = json.load(f)
                return status.get(username, {}).get("password_changed", False)
        except:
            pass
    return False


def login_required(f):
    """Login check decorator - uses auth.login_required but redirects to page route."""
    return auth_login_required(f)


@pages_bp.route("/login")
def login_page():
    """Login page."""
    if "username" in session:
        return redirect(url_for("pages.dashboard"))
    return render_template('login.html')


@pages_bp.route("/force-change-password")
@login_required
def force_change_password_page():
    """First login password change page."""
    username = session.get("username")
    if is_user_password_changed(username):
        return redirect(url_for("pages.dashboard"))
    return render_template('force_change_password.html')


@pages_bp.route("/dashboard")
@login_required
def dashboard():
    """Main dashboard."""
    return render_template('dashboard.html')


@pages_bp.route("/")
def index():
    """Homepage redirect."""
    if "username" in session:
        username = session.get("username")
        if not is_user_password_changed(username):
            return redirect(url_for("pages.force_change_password_page"))
        return redirect(url_for("pages.dashboard"))
    return redirect(url_for("pages.login_page"))