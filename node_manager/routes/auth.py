"""
Auth routes - Authentication and user management with bcrypt.
"""

from flask import request, jsonify, redirect, url_for, session
from functools import wraps
from routes import auth_bp
from models.user import User


def is_first_time() -> bool:
    """Check if this is first time setup (no users in database)."""
    return len(User.get_all()) == 0


def login_required(f):
    """Login required decorator - redirects to pages.login_page."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("pages.login_page"))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """Admin required decorator."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("auth.login"))
        from models.user import User
        user = User.get_by_username(session.get("username"))
        if not user or user.role != "admin":
            return jsonify({"success": False, "error": "Admin access required"}), 403
        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route("/api/login", methods=["POST"])
def login():
    """User login."""
    # First time setup check
    if is_first_time():
        return jsonify(
            {
                "success": False,
                "error": "first_time_setup",
                "message": "请先创建管理员账户",
            }
        )

    data = request.json
    username = data.get("username", "")
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"success": False, "error": "请输入用户名和密码"})

    user = User.authenticate(username, password)
    if user:
        session["username"] = user.username
        # Check if user must change password
        if user.must_change_password:
            return jsonify(
                {
                    "success": True,
                    "must_change_password": True,
                    "message": "首次登录必须修改密码",
                }
            )
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "用户名或密码错误"})


@auth_bp.route("/api/setup", methods=["POST"])
def setup():
    """First time setup - create admin account."""
    if not is_first_time():
        return jsonify({"success": False, "error": "系统已设置，请登录"})

    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")

    # Validation
    if not username or not password:
        return jsonify({"success": False, "error": "用户名和密码不能为空"})

    if len(username) < 3:
        return jsonify({"success": False, "error": "用户名至少3个字符"})

    if len(password) < 8:
        return jsonify({"success": False, "error": "密码至少8个字符"})

    if password != confirm_password:
        return jsonify({"success": False, "error": "两次输入的密码不一致"})

    if password.lower() in ["password", "12345678", "admin123"]:
        return jsonify({"success": False, "error": "密码强度太弱，请使用更复杂的密码"})

    # Create admin user
    try:
        user = User.create_user(username=username, password=password, role="admin")
        session["username"] = user.username
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": "Failed to create user"})


@auth_bp.route("/api/check-setup-status", methods=["GET"])
def check_setup_status():
    """Check if system needs setup."""
    return jsonify({"needs_setup": is_first_time()})


@auth_bp.route("/api/logout")
def logout():
    """User logout."""
    session.pop("username", None)
    return redirect(url_for("pages.login_page"))


@auth_bp.route("/api/user-info")
@login_required
def user_info():
    """Get current user info."""
    username = session.get("username")
    user = User.get_by_username(username)
    if user:
        return jsonify(
            {
                "username": user.username,
                "role": user.role,
                "must_change_password": user.must_change_password,
            }
        )
    return jsonify({"username": username})


@auth_bp.route("/api/change-password", methods=["POST"])
@login_required
def change_password():
    """Change current user password."""
    data = request.json
    username = session.get("username")
    user = User.get_by_username(username)

    if not user:
        return jsonify({"success": False, "error": "用户不存在"})

    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")

    if len(new_password) < 8:
        return jsonify({"success": False, "error": "密码至少8个字符"})

    if new_password != confirm_password:
        return jsonify({"success": False, "error": "两次输入的密码不一致"})

    if not user.check_password(current_password):
        return jsonify({"success": False, "error": "当前密码错误"})

    if new_password.lower() in ["password", "12345678", "admin123"]:
        return jsonify({"success": False, "error": "密码强度太弱"})

    user.password_hash = User.hash_password(new_password)
    user.clear_must_change_password()

    return jsonify({"success": True, "message": "密码修改成功"})


@auth_bp.route("/api/users", methods=["GET", "POST"])
@login_required
def users_api():
    """Get all users or create a new user."""
    if request.method == "GET":
        users = User.get_all()
        return jsonify([u.to_dict() for u in users])

    if request.method == "POST":
        # Admin only for creating users
        current_user = User.get_by_username(session.get("username"))
        if not current_user or current_user.role != "admin":
            return jsonify({"success": False, "error": "Admin access required"}), 403

        data = request.json
        username = data.get("username", "").strip()
        password = data.get("password", "")
        role = data.get("role", "user")

        if not username or not password:
            return jsonify({"success": False, "error": "用户名和密码不能为空"})

        if len(username) < 3:
            return jsonify({"success": False, "error": "用户名至少3个字符"})

        if len(password) < 8:
            return jsonify({"success": False, "error": "密码至少8个字符"})

        if User.get_by_username(username):
            return jsonify({"success": False, "error": "用户已存在"})

        try:
            User.create_user(username=username, password=password, role=role)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": "Failed to create user"})


@auth_bp.route("/api/users/<username>", methods=["DELETE"])
@login_required
def delete_user(username):
    """Delete a user. Admin only."""
    current_user = User.get_by_username(session.get("username"))
    if not current_user or current_user.role != "admin":
        return jsonify({"success": False, "error": "Admin access required"}), 403

    if username == current_user.username:
        return jsonify({"success": False, "error": "不能删除自己"})

    user = User.get_by_username(username)
    if not user:
        return jsonify({"success": False, "error": "用户不存在"})

    User.delete_by_id(user.id)
    return jsonify({"success": True})


@auth_bp.route("/api/users-admin-change-password", methods=["POST"])
@login_required
def users_admin_change_password():
    """Admin change user password. Admin only."""
    current_user = User.get_by_username(session.get("username"))
    if not current_user or current_user.role != "admin":
        return jsonify({"success": False, "error": "Admin access required"}), 403

    data = request.json
    username = data.get("username", "")
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")

    if not username or not new_password:
        return jsonify({"success": False, "error": "用户名和密码不能为空"})

    user = User.get_by_username(username)
    if not user:
        return jsonify({"success": False, "error": "用户不存在"})

    if len(new_password) < 8:
        return jsonify({"success": False, "error": "密码至少8个字符"})

    if new_password != confirm_password:
        return jsonify({"success": False, "error": "两次输入的密码不一致"})

    user.password_hash = User.hash_password(new_password)
    user.save()

    return jsonify({"success": True})


@auth_bp.route("/api/force-change-password", methods=["POST"])
@login_required
def force_change_password():
    """首次登录强制修改密码"""
    # Lazy import to avoid circular dependency
    import app
    data = request.json
    users = app.load_users()
    username = session.get("username")

    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if users.get(username) != current_password:
        return jsonify({"success": False, "error": "Current password is incorrect"})

    users[username] = new_password
    app.save_users(users)
    app.mark_password_as_changed(username)

    return jsonify({"success": True})
