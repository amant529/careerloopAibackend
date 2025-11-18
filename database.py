import sqlite3

DB = "careerloop.db"

def connect():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    conn = connect()
    cur = conn.cursor()

    # Create analytics tables if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_id TEXT,
            page TEXT,
            ts TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_id TEXT,
            email TEXT,
            event_type TEXT,
            ts TEXT
        )
    """)

    conn.commit()
    conn.close()


# === NEW FUNCTIONS (Fixing error) ===

def save_visit(visitor_id, page, ts):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO visits (visitor_id, page, ts) VALUES (?, ?, ?)",
                (visitor_id, page, ts))
    conn.commit()
    conn.close()

def save_event(visitor_id, email, event_type, ts):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO events (visitor_id, email, event_type, ts) VALUES (?, ?, ?, ?)",
                (visitor_id, email, event_type, ts))
    conn.commit()
    conn.close()
