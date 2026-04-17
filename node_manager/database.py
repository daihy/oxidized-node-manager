"""
Database module - SQLite connection and initialization.
"""

import sqlite3
import os
import csv
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

DATABASE_PATH = os.environ.get("DATABASE_PATH", "/oxidized_config/nodes.db")
CONFIG_FILE = os.environ.get("CONFIG_FILE", "/oxidized_config/nodes.csv")


def get_db_path() -> str:
    """Get the database file path."""
    return DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """Create a database connection."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db_cursor():
    """Context manager for database cursor."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database():
    """Initialize the database with required tables and default admin user."""
    with get_db_cursor() as cursor:
        # Nodes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                ip TEXT NOT NULL,
                model TEXT NOT NULL,
                protocol TEXT NOT NULL DEFAULT 'ssh',
                port INTEGER NOT NULL DEFAULT 22,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                last_backup TEXT,
                last_status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'admin',
                must_change_password INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)

        # Sync log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TEXT DEFAULT (datetime('now'))
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_name ON nodes(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_ip ON nodes(ip)")

    # Create default admin user if no users exist
    _create_default_admin_user()


def log_sync(action: str, details: Optional[str] = None):
    """Log a sync operation."""
    with get_db_cursor() as cursor:
        cursor.execute(
            "INSERT INTO sync_log (action, details) VALUES (?, ?)", (action, details)
        )


def _create_default_admin_user():
    """Create default admin user if no users exist."""
    import bcrypt

    # Check if any users exist
    with get_db_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]

    if count > 0:
        return  # Users already exist, skip

    # Get default password from environment variable or use a secure default
    default_password = os.environ.get("ADMIN_DEFAULT_PASSWORD", "admin123")

    # Hash the password
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(default_password.encode("utf-8"), salt).decode(
        "utf-8"
    )

    # Create admin user
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, role, must_change_password)
            VALUES (?, ?, ?, 1)
            """,
            ("admin", password_hash, "admin"),
        )

    print(f"Default admin user created with password: {default_password}")
    print("IMPORTANT: Please change this password after first login!")


def get_all_nodes() -> List[Dict[str, Any]]:
    """Get all nodes from database."""
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT name, ip, model, protocol, port, username, password FROM nodes"
        )
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def ensure_csv_synced() -> bool:
    """
    Ensure CSV file is in sync with SQLite database.
    Called at startup to prevent git checkout or other issues from breaking Oxidized.

    Returns True if CSV was written, False if already in sync or failed.
    """
    try:
        # Read current CSV content (if exists)
        current_csv_nodes = []
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                current_csv_nodes = list(reader)

        # Get nodes from database
        db_nodes = get_all_nodes()

        # Compare by name+ip+model (key fields)
        def node_key(n):
            return f"{n.get('name', '')}|{n.get('ip', '')}|{n.get('model', '')}"

        csv_keys = {node_key(n) for n in current_csv_nodes}
        db_keys = {node_key(n) for n in db_nodes}

        # If different, sync CSV from database
        if csv_keys != db_keys:
            print(
                f"CSV sync needed: {len(csv_keys)} CSV nodes, {len(db_keys)} DB nodes"
            )
            _write_csv_from_db(db_nodes)
            return True
        else:
            print(f"CSV already in sync: {len(db_keys)} nodes")
            return False

    except Exception as e:
        print(f"Error ensuring CSV sync: {e}")
        return False


def _write_csv_from_db(nodes: List[Dict[str, Any]]):
    """Write nodes from database to CSV file."""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["name", "ip", "model", "protocol", "port", "username", "password"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for node in nodes:
            writer.writerow(
                {
                    "name": node.get("name", ""),
                    "ip": node.get("ip", ""),
                    "model": node.get("model", "").lower() if node.get("model") else "",
                    "protocol": node.get("protocol", "ssh"),
                    "port": node.get("port", 22),
                    "username": node.get("username", ""),
                    "password": node.get("password", ""),
                }
            )
    print(f"CSV written with {len(nodes)} nodes to {CONFIG_FILE}")


if __name__ == "__main__":
    # Initialize database when run directly
    init_database()
    print(f"Database initialized at: {get_db_path()}")
