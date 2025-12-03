import sqlite3
import os

DB_FILE = "loots.db"

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS loots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    loot_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    type TEXT NOT NULL,
    file_id TEXT,
    link TEXT,
    text_msg TEXT
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")
conn.commit()


def add_user(uid):
    try:
        c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))
        conn.commit()
    except Exception:
        pass


def get_users():
    c.execute("SELECT user_id FROM users")
    return [row[0] for row in c.fetchall()]


def add_loot(title, description):
    c.execute("INSERT INTO loots (title, description) VALUES (?,?)", (title, description))
    conn.commit()
    return c.lastrowid


def get_loots():
    c.execute("SELECT id, title, description FROM loots")
    return c.fetchall()


def get_loot(loot_id):
    c.execute("SELECT id, title, description FROM loots WHERE id=?", (loot_id,))
    return c.fetchone()


def delete_loot(loot_id):
    c.execute("DELETE FROM loots WHERE id=?", (loot_id,))
    c.execute("DELETE FROM media WHERE loot_id=?", (loot_id,))
    conn.commit()


def add_media(loot_id, kind, mtype, file_id=None, link=None, text_msg=None):
    c.execute(
        "INSERT INTO media (loot_id, kind, type, file_id, link, text_msg) VALUES (?,?,?,?,?,?)",
        (loot_id, kind, mtype, file_id, link, text_msg),
    )
    conn.commit()
    return c.lastrowid


def get_media(loot_id, kind=None):
    if kind:
        c.execute(
            "SELECT id, kind, type, file_id, link, text_msg FROM media WHERE loot_id=? AND kind=?",
            (loot_id, kind),
        )
    else:
        c.execute(
            "SELECT id, kind, type, file_id, link, text_msg FROM media WHERE loot_id=?",
            (loot_id,),
        )
    return c.fetchall()


def delete_media(media_id):
    c.execute("DELETE FROM media WHERE id=?", (media_id,))
    conn.commit()


def get_media_by_id(media_id):
    c.execute("SELECT loot_id, kind, type, file_id, link, text_msg FROM media WHERE id=?", (media_id,))
    return c.fetchone()