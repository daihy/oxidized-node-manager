"""
Tests for authentication routes.
"""

import pytest
import json


class TestSetupStatus:
    """Tests for setup status endpoint."""

    def test_check_setup_status_no_users(self, client, clean_db):
        """Test that needs_setup returns true when no users exist."""
        response = client.get("/api/check-setup-status")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["needs_setup"] is True

    def test_check_setup_status_with_users(self, client, test_user):
        """Test that needs_setup returns false when users exist."""
        response = client.get("/api/check-setup-status")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["needs_setup"] is False


class TestSetup:
    """Tests for first-time setup."""

    def test_setup_creates_admin_user(self, client, clean_db):
        """Test that setup creates the admin user."""
        response = client.post(
            "/api/setup",
            json={
                "username": "admin",
                "password": "SecureAdmin123!",
                "confirm_password": "SecureAdmin123!",
            },
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

        # Verify user can login
        response = client.post(
            "/api/login",
            json={"username": "admin", "password": "SecureAdmin123!"},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_setup_requires_password_confirmation(self, client, clean_db):
        """Test that password confirmation must match."""
        response = client.post(
            "/api/setup",
            json={
                "username": "admin",
                "password": "SecureAdmin123!",
                "confirm_password": "DifferentPass123!",
            },
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False
        assert "不一致" in data["error"]

    def test_setup_rejects_short_password(self, client, clean_db):
        """Test that passwords under 8 characters are rejected."""
        response = client.post(
            "/api/setup",
            json={
                "username": "admin",
                "password": "short",
                "confirm_password": "short",
            },
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False
        assert "8" in data["error"]

    def test_setup_rejects_weak_password(self, client, clean_db):
        """Test that weak passwords are rejected."""
        response = client.post(
            "/api/setup",
            json={
                "username": "admin",
                "password": "admin123",
                "confirm_password": "admin123",
            },
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False
        assert "强度" in data["error"]

    def test_setup_fails_when_already_configured(self, client, test_user):
        """Test that setup fails when users already exist."""
        response = client.post(
            "/api/setup",
            json={
                "username": "newadmin",
                "password": "SecureAdmin123!",
                "confirm_password": "SecureAdmin123!",
            },
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False
        assert "已设置" in data["error"]


class TestLogin:
    """Tests for login endpoint."""

    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/api/login",
            json={"username": "testuser", "password": "TestPass123!"},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password."""
        response = client.post(
            "/api/login",
            json={"username": "testuser", "password": "wrongpassword"},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False

    def test_login_nonexistent_user(self, client, clean_db):
        """Test login with nonexistent user."""
        response = client.post(
            "/api/login",
            json={"username": "nobody", "password": "anypassword"},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False

    def test_login_empty_credentials(self, client, clean_db):
        """Test login with empty credentials."""
        response = client.post(
            "/api/login",
            json={"username": "", "password": ""},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False


class TestLogout:
    """Tests for logout endpoint."""

    def test_logout_clears_session(self, client, test_client_with_auth):
        """Test that logout clears the session."""
        response = test_client_with_auth.get("/api/logout")
        # Should redirect
        assert response.status_code in [302, 200]


class TestUserInfo:
    """Tests for user info endpoint."""

    def test_user_info_requires_auth(self, client):
        """Test that user info requires authentication."""
        response = client.get("/api/user-info")
        # Should redirect to login
        assert response.status_code == 302

    def test_user_info_returns_username(self, client, test_client_with_auth):
        """Test that user info returns the logged-in username."""
        response = test_client_with_auth.get("/api/user-info")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["username"] == "testuser"


class TestChangePassword:
    """Tests for change password endpoint."""

    def test_change_password_success(self, client, test_client_with_auth):
        """Test successful password change."""
        response = test_client_with_auth.post(
            "/api/change-password",
            json={
                "current_password": "TestPass123!",
                "new_password": "NewPass456!",
                "confirm_password": "NewPass456!",
            },
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

        # Verify new password works
        response = client.post(
            "/api/login",
            json={"username": "testuser", "password": "NewPass456!"},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_change_password_wrong_current(self, client, test_client_with_auth):
        """Test password change with wrong current password."""
        response = test_client_with_auth.post(
            "/api/change-password",
            json={
                "current_password": "WrongPass!",
                "new_password": "NewPass456!",
                "confirm_password": "NewPass456!",
            },
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False
        assert "错误" in data["error"]


class TestUsersManagement:
    """Tests for users management endpoints."""

    def test_list_users(self, client, test_client_with_auth):
        """Test listing users."""
        response = test_client_with_auth.get("/api/users")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
        assert any(u["username"] == "testuser" for u in data)

    def test_create_user(self, client, test_client_with_auth):
        """Test creating a new user."""
        response = test_client_with_auth.post(
            "/api/users",
            json={
                "username": "newuser",
                "password": "NewUser123!",
                "role": "user",
            },
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_create_duplicate_user(self, client, test_client_with_auth):
        """Test creating duplicate user fails."""
        response = test_client_with_auth.post(
            "/api/users",
            json={
                "username": "testuser",  # Already exists
                "password": "SomePass123!",
                "role": "user",
            },
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False

    def test_delete_user(self, client, test_client_with_auth):
        """Test deleting a user."""
        # Create a user to delete
        test_client_with_auth.post(
            "/api/users",
            json={"username": "todelete", "password": "ToDelete123!", "role": "user"},
        )
        response = test_client_with_auth.delete("/api/users/todelete")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

    def test_cannot_delete_self(self, client, test_client_with_auth):
        """Test that user cannot delete themselves."""
        response = test_client_with_auth.delete("/api/users/testuser")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False
        assert "自己" in data["error"]
