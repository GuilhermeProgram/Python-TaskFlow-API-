"""
models.py - Modelos de dados (User e Task)
"""

import hashlib
import secrets
from datetime import datetime


def hash_password(password: str) -> str:
    """Gera hash seguro da senha."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(stored: str, password: str) -> bool:
    """Verifica senha contra o hash armazenado."""
    salt, hashed = stored.split(':')
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest() == hashed


class UserModel:
    def __init__(self, db):
        self.db = db

    def create(self, username: str, password: str) -> int:
        hashed = hash_password(password)
        cursor = self.db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed)
        )
        self.db.commit()
        return cursor.lastrowid

    def find_by_username(self, username: str):
        row = self.db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        return dict(row) if row else None

    def authenticate(self, username: str, password: str):
        user = self.find_by_username(username)
        if user and verify_password(user['password'], password):
            return user
        return None


class TaskModel:
    def __init__(self, db):
        self.db = db

    def create(self, user_id, title, description='', priority='medium', due_date=None) -> int:
        cursor = self.db.execute(
            """INSERT INTO tasks (user_id, title, description, priority, due_date)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, title, description, priority, due_date)
        )
        self.db.commit()
        return cursor.lastrowid

    def get_all(self, user_id, status=None, priority=None):
        query = "SELECT * FROM tasks WHERE user_id = ?"
        params = [user_id]

        if status:
            query += " AND status = ?"
            params.append(status)
        if priority:
            query += " AND priority = ?"
            params.append(priority)

        query += " ORDER BY created_at DESC"
        rows = self.db.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_by_id(self, task_id, user_id):
        row = self.db.execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id)
        ).fetchone()
        return dict(row) if row else None

    def update(self, task_id, user_id, data: dict):
        allowed = {'title', 'description', 'status', 'priority', 'due_date'}
        fields = {k: v for k, v in data.items() if k in allowed}

        if not fields:
            return

        fields['updated_at'] = datetime.utcnow().isoformat()
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [task_id, user_id]

        self.db.execute(
            f"UPDATE tasks SET {set_clause} WHERE id = ? AND user_id = ?",
            values
        )
        self.db.commit()

    def delete(self, task_id, user_id):
        self.db.execute(
            "DELETE FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id)
        )
        self.db.commit()

    def get_stats(self, user_id) -> dict:
        rows = self.db.execute(
            """SELECT status, COUNT(*) as count
               FROM tasks WHERE user_id = ?
               GROUP BY status""",
            (user_id,)
        ).fetchall()

        stats = {'pending': 0, 'in_progress': 0, 'done': 0, 'total': 0}
        for row in rows:
            stats[row['status']] = row['count']
            stats['total'] += row['count']

        # prioridade alta pendente
        high = self.db.execute(
            "SELECT COUNT(*) as c FROM tasks WHERE user_id = ? AND priority = 'high' AND status != 'done'",
            (user_id,)
        ).fetchone()
        stats['high_priority_pending'] = high['c']

        return stats
