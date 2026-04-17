"""
Node model - Pure SQL operations for nodes.
"""

from typing import List, Optional, Dict, Any
from database import get_db_cursor, get_connection


class Node:
    """Node model representing a network device."""

    def __init__(
        self,
        name: str,
        ip: str,
        model: str,
        protocol: str = "ssh",
        port: int = 22,
        username: str = "",
        password: str = "",
        last_backup: Optional[str] = None,
        last_status: str = "pending",
        id: Optional[int] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.ip = ip
        self.model = model
        self.protocol = protocol
        self.port = port
        self.username = username
        self.password = password
        self.last_backup = last_backup
        self.last_status = last_status
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "ip": self.ip,
            "model": self.model,
            "protocol": self.protocol,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "last_backup": self.last_backup,
            "last_status": self.last_status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_row(cls, row) -> "Node":
        """Create Node from database row (sqlite3.Row or dict)."""
        # sqlite3.Row doesn't have .get() method, so we use dict() to convert
        if hasattr(row, "keys"):
            data = dict(row)
        else:
            data = row
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            ip=data.get("ip", ""),
            model=data.get("model", ""),
            protocol=data.get("protocol", "ssh"),
            port=data.get("port", 22),
            username=data.get("username", ""),
            password=data.get("password", ""),
            last_backup=data.get("last_backup"),
            last_status=data.get("last_status", "pending"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    @classmethod
    def get_all(cls) -> List["Node"]:
        """Get all nodes."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM nodes ORDER BY name")
            return [cls.from_row(row) for row in cursor.fetchall()]

    @classmethod
    def get_by_id(cls, node_id: int) -> Optional["Node"]:
        """Get node by ID."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM nodes WHERE id = ?", (node_id,))
            row = cursor.fetchone()
            return cls.from_row(row) if row else None

    @classmethod
    def get_by_name(cls, name: str) -> Optional["Node"]:
        """Get node by name."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM nodes WHERE name = ?", (name,))
            row = cursor.fetchone()
            return cls.from_row(row) if row else None

    def save(self) -> "Node":
        """Insert or update the node."""
        with get_db_cursor() as cursor:
            if self.id is None:
                # Insert new node
                cursor.execute(
                    """
                    INSERT INTO nodes (name, ip, model, protocol, port, username, password, last_backup, last_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        self.name,
                        self.ip,
                        self.model,
                        self.protocol,
                        self.port,
                        self.username,
                        self.password,
                        self.last_backup,
                        self.last_status,
                    ),
                )
                self.id = cursor.lastrowid
            else:
                # Update existing node
                cursor.execute(
                    """
                    UPDATE nodes SET
                        name=?, ip=?, model=?, protocol=?, port=?,
                        username=?, password=?, last_backup=?, last_status=?,
                        updated_at=datetime('now')
                    WHERE id=?
                """,
                    (
                        self.name,
                        self.ip,
                        self.model,
                        self.protocol,
                        self.port,
                        self.username,
                        self.password,
                        self.last_backup,
                        self.last_status,
                        self.id,
                    ),
                )
        return self

    def delete(self) -> bool:
        """Delete the node."""
        if self.id is None:
            return False
        with get_db_cursor() as cursor:
            cursor.execute("DELETE FROM nodes WHERE id=?", (self.id,))
            return cursor.rowcount > 0

    @classmethod
    def delete_by_id(cls, node_id: int) -> bool:
        """Delete node by ID."""
        with get_db_cursor() as cursor:
            cursor.execute("DELETE FROM nodes WHERE id=?", (node_id,))
            return cursor.rowcount > 0

    @classmethod
    def update_status(
        cls, node_id: int, status: str, last_backup: Optional[str] = None
    ):
        """Update node backup status."""
        with get_db_cursor() as cursor:
            if last_backup:
                cursor.execute(
                    'UPDATE nodes SET last_status=?, last_backup=?, updated_at=datetime("now") WHERE id=?',
                    (status, last_backup, node_id),
                )
            else:
                cursor.execute(
                    'UPDATE nodes SET last_status=?, updated_at=datetime("now") WHERE id=?',
                    (status, node_id),
                )

    @classmethod
    def count(cls) -> int:
        """Get total node count."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM nodes")
            return cursor.fetchone()["count"]

    @classmethod
    def search(cls, query: str) -> List["Node"]:
        """Search nodes by name or IP."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM nodes WHERE name LIKE ? OR ip LIKE ? ORDER BY name",
                (f"%{query}%", f"%{query}%"),
            )
            return [cls.from_row(row) for row in cursor.fetchall()]

    @classmethod
    def get_by_status(cls, status: str) -> List["Node"]:
        """Get nodes by backup status."""
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM nodes WHERE last_status=? ORDER BY name", (status,)
            )
            return [cls.from_row(row) for row in cursor.fetchall()]
