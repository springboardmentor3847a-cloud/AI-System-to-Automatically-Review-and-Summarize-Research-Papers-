import sqlite3
from datetime import datetime

DB_NAME = "research_ai.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password_hash TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT, topic TEXT, summary TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

def add_user(username, password_hash):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?, ?)", (username, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username=?", (username,))
    res = c.fetchone()
    conn.close()
    return res

# --- NEW: Delete User & History ---
def delete_user(username):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        # Delete user record
        c.execute("DELETE FROM users WHERE username=?", (username,))
        # Delete user history
        c.execute("DELETE FROM history WHERE username=?", (username,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def save_research(username, topic, summary):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO history (username, topic, summary, timestamp) VALUES (?, ?, ?, ?)",
              (username, topic, summary, datetime.now()))
    conn.commit()
    conn.close()

def get_history(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT topic, timestamp FROM history WHERE username=? ORDER BY timestamp DESC", (username,))
    rows = c.fetchall()
    conn.close()
    return rows

init_db()