"""
Group model - Pure SQL operations for groups.
"""
from typing import List, Optional, Dict, Any
from database import get_db_cursor


class Group:
    def __init__(self, name: str, description: str = "", id: Optional[int] = None, created_at: Optional[str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.created_at = created_at

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "description": self.description, "created_at": self.created_at}

    @classmethod
    def from_row(cls, row) -> "Group":
        if hasattr(row, "keys"):
            data = dict(row)
        else:
            data = row
        return cls(id=data.get("id"), name=data.get("name", ""), description=data.get("description", ""), created_at=data.get("created_at"))

    @classmethod
    def get_all(cls) -> List["Group"]:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM groups ORDER BY id ASC")
            return [cls.from_row(row) for row in cursor.fetchall()]

    @classmethod
    def get_by_id(cls, group_id: int) -> Optional["Group"]:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM groups WHERE id = ?", (group_id,))
            row = cursor.fetchone()
            return cls.from_row(row) if row else None

    @classmethod
    def get_by_name(cls, name: str) -> Optional["Group"]:
        """Find group by name (case-insensitive)."""
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM groups WHERE LOWER(name) = LOWER(?)", (name,))
            row = cursor.fetchone()
            return cls.from_row(row) if row else None

    def save(self) -> "Group":
        with get_db_cursor() as cursor:
            if self.id is None:
                cursor.execute("INSERT INTO groups (name, description) VALUES (?, ?)", (self.name, self.description))
                self.id = cursor.lastrowid
            else:
                cursor.execute("UPDATE groups SET name=?, description=? WHERE id=?", (self.name, self.description, self.id))
        return self

    def delete(self) -> bool:
        if self.id is None:
            return False
        with get_db_cursor() as cursor:
            cursor.execute("DELETE FROM groups WHERE id=?", (self.id,))
            return cursor.rowcount > 0
