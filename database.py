import sqlite3

DB = "careerloop.db"

def connect():
    return sqlite3.connect(DB, check_same_thread=False)

### Initialize DB
def init_db():
    conn = connect()
    cur = conn.cursor()

    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            otp TEXT,
            resume TEXT
        )
    """)

    # Visits analytics
    cur.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_id TEXT,
            page TEXT,
            ts TEXT
        )
    """)

    # Events analytics
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

### Utility DB Session For Routers
def get_session():
    """Return DB connection & cursor for transactional use."""
    conn = connect()
    cur = conn.cursor()
    return conn, cur

### Resume Data
def save_resume(email, resume):
    conn, cur = get_session()
    cur.execute("UPDATE users SET resume = ? WHERE email = ?", (resume, email))
    conn.commit()
    conn.close()

def fetch_resume(email):
    conn, cur = get_session()
    cur.execute("SELECT resume FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

### Analytics
def save_visit(visitor_id, page, ts):
    conn, cur = get_session()
    cur.execute("INSERT INTO visits (visitor_id, page, ts) VALUES (?, ?, ?)",
                (visitor_id, page, ts))
    conn.commit()
    conn.close()

def save_event(visitor_id, email, event_type, ts):
    conn, cur = get_session()
    cur.execute("INSERT INTO events (visitor_id, email, event_type, ts) VALUES (?, ?, ?, ?)",
                (visitor_id, email, event_type, ts))
    conn.commit()
    conn.close()
