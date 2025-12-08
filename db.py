import sqlite3
import os

DB_FILE = "loots.db"

conn = sqlite3.connect(DB_FILE, check_same_thread=False)



cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS loots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT
)
""")
cur.execute("""
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
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY
)
""")
conn.commit()
cur.close()



def add_user(uid):
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))
    conn.commit()
    cur.close()


def get_users():
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    rows = cur.fetchall()
    cur.close()
    return [r[0] for r in rows]



def add_loot(title, description):
    cur = conn.cursor()
    cur.execute("INSERT INTO loots (title, description) VALUES (?, ?)", (title, description))
    conn.commit()
    loot_id = cur.lastrowid
    cur.close()
    return loot_id


def get_loots():
    cur = conn.cursor()
    cur.execute("SELECT id, title, description FROM loots")
    rows = cur.fetchall()
    cur.close()
    return rows


def get_loot(loot_id):
    cur = conn.cursor()
    cur.execute("SELECT id, title, description FROM loots WHERE id=?", (loot_id,))
    row = cur.fetchone()
    cur.close()
    return row


def delete_loot(loot_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM loots WHERE id=?", (loot_id,))
    cur.execute("DELETE FROM media WHERE loot_id=?", (loot_id,))
    conn.commit()
    cur.close()



def add_media(loot_id, kind, mtype, file_id=None, link=None, text_msg=None):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO media (loot_id, kind, type, file_id, link, text_msg) VALUES (?,?,?,?,?,?)",
        (loot_id, kind, mtype, file_id, link, text_msg),
    )
    conn.commit()
    media_id = cur.lastrowid
    cur.close()
    return media_id


def get_media(loot_id, kind=None):
    cur = conn.cursor()
    if kind:
        cur.execute(
            "SELECT id, kind, type, file_id, link, text_msg FROM media WHERE loot_id=? AND kind=?",
            (loot_id, kind),
        )
    else:
        cur.execute(
            "SELECT id, kind, type, file_id, link, text_msg FROM media WHERE loot_id=?",
            (loot_id,),
        )
    rows = cur.fetchall()
    cur.close()
    return rows


def delete_media(media_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM media WHERE id=?", (media_id,))
    conn.commit()
    cur.close()


def get_media_by_id(media_id):
    cur = conn.cursor()
    cur.execute("SELECT loot_id, kind, type, file_id, link, text_msg FROM media WHERE id=?", (media_id,))
    row = cur.fetchone()
    cur.close()
    return row



def add_admin(uid):
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (uid,))
    conn.commit()
    cur.close()


def remove_admin(uid):
    cur = conn.cursor()
    cur.execute("DELETE FROM admins WHERE user_id=?", (uid,))
    conn.commit()
    cur.close()


def get_admins():
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM admins")
    rows = cur.fetchall()
    cur.close()
    return [r[0] for r in rows]
