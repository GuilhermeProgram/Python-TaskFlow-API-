"""
database.py - Configuração e inicialização do banco SQLite
"""

import sqlite3
import os

DB_PATH = 'taskflow.db'


def get_db():
    """Retorna conexão com o banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permite acesso por nome de coluna
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Cria as tabelas se não existirem."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            title       TEXT    NOT NULL,
            description TEXT    DEFAULT '',
            status      TEXT    DEFAULT 'pending',   -- pending | in_progress | done
            priority    TEXT    DEFAULT 'medium',    -- low | medium | high
            due_date    TEXT,
            created_at  TEXT    DEFAULT (datetime('now')),
            updated_at  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()
    print("✅ Banco de dados inicializado.")
