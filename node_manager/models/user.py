"""
User model - Pure SQL operations for users with bcrypt password hashing.
"""

from typing import List, Optional, Dict, Any
import bcrypt
from database import get_db_cursor


class User:
    """User model for authentication."""

    def __init__(
        self,
        username: str,
        password_hash: str = "",
        role: str = "admin",
        id: Optional[int] = None,
        created_at: Optional[str] = None,
        must_change_password: bool = False,
    ):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at
        self.must_change_password = must_change_password

    def to_dict(self, include_hash: bool = False) -> Dict[str, Any]:
        """Convert user to dictionary."""
        data = {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "must_change_password": self.must_change_password,
            "created_at": self.created_at,
        }
        if include_hash:
            data["password_hash"] = self.password_hash
        return data

    @classmethod
    def from_row(cls, row) -> "User":
        """Create User from database row."""
        # sqlite3.Row doesn't have .get() method, so we use dict() to convert
        if hasattr(row, "keys"):
            data = dict(row)
        else:
            data = row
        return cls(
            id=data.get("id"),
            username=data.get("username", ""),
            password_hash=data.get("password_hash", ""),
            role=data.get("role", "admin"),
            created_at=data.get("created_at"),
            must_change_password=bool(data.get("must_change_password", 0)),
        )

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Verify password against hash."""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    @classmethod
    def get_all(cls) -> List["User"]:
        """Get all users."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM users ORDER BY username")
            return [cls.from_row(row) for row in cursor.fetchall()]

    @classmethod
    def get_by_id(cls, user_id: int) -> Optional["User"]:
        """Get user by ID."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return cls.from_row(row) if row else None

    @classmethod
    def get_by_username(cls, username: str) -> Optional["User"]:
        """Get user by username."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return cls.from_row(row) if row else None

    def save(self) -> "User":
        """Insert or update the user."""
        with get_db_cursor() as cursor:
            if self.id is None:
                # Insert new user
                cursor.execute(
                    """
                    INSERT INTO users (username, password_hash, role, must_change_password)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        self.username,
                        self.password_hash,
                        self.role,
                        int(self.must_change_password),
                    ),
                )
                self.id = cursor.lastrowid
            else:
                # Update existing user
                cursor.execute(
                    """
                    UPDATE users SET username=?, password_hash=?, role=?, must_change_password=?
                    WHERE id=?
                """,
                    (
                        self.username,
                        self.password_hash,
                        self.role,
                        int(self.must_change_password),
                        self.id,
                    ),
                )
        return self

    def clear_must_change_password(self) -> "User":
        """Clear the must_change_password flag after user changes password."""
        self.must_change_password = False
        return self.save()

    def delete(self) -> bool:
        """Delete the user."""
        if self.id is None:
            return False
        with get_db_cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id=?", (self.id,))
            return cursor.rowcount > 0

    @classmethod
    def delete_by_id(cls, user_id: int) -> bool:
        """Delete user by ID."""
        with get_db_cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            return cursor.rowcount > 0

    @classmethod
    def authenticate(cls, username: str, password: str) -> Optional["User"]:
        """Authenticate user with username and password."""
        user = cls.get_by_username(username)
        if user and user.check_password(password):
            return user
        return None

    @classmethod
    def create_user(
        cls,
        username: str,
        password: str,
        role: str = "admin",
        must_change_password: bool = False,
    ) -> "User":
        """Create a new user with hashed password."""
        user = cls(
            username=username,
            password_hash=cls.hash_password(password),
            role=role,
            must_change_password=must_change_password,
        )
        return user.save()
