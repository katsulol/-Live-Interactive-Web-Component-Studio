"""SQLite database layer for Live Interactive Multi-Language Code Studio."""
import sqlite3
from typing import List, Dict, Optional, Any
from datetime import datetime

DB_FILE = "studio.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                language TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                version_number INTEGER NOT NULL,
                prompt TEXT NOT NULL,
                code TEXT NOT NULL,
                language TEXT NOT NULL,
                output TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        conn.commit()

def create_project(name: str, language: str) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO projects (name, language, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (name, language)
        )
        conn.commit()
        return cursor.lastrowid

def list_projects() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.name, p.language, p.created_at, p.updated_at,
                   COUNT(v.id) as version_count
            FROM projects p
            LEFT JOIN versions v ON p.id = v.project_id
            GROUP BY p.id
            ORDER BY p.updated_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

def get_project(project_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def delete_project(project_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM versions WHERE project_id = ?", (project_id,))
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()

def add_version(project_id: int, prompt: str, code: str, language: str, output: str = "") -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COALESCE(MAX(version_number), 0) + 1 FROM versions WHERE project_id = ?",
            (project_id,)
        )
        next_version = cursor.fetchone()[0]
        
        cursor.execute(
            """INSERT INTO versions (project_id, version_number, prompt, code, language, output, created_at)
               VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (project_id, next_version, prompt, code, language, output)
        )
        cursor.execute(
            "UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (project_id,)
        )
        conn.commit()
        return next_version

def get_versions(project_id: int) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM versions WHERE project_id = ? ORDER BY version_number ASC",
            (project_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def get_latest_version(project_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM versions WHERE project_id = ? ORDER BY version_number DESC LIMIT 1",
            (project_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
