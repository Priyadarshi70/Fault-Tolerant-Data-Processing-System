import sqlite3, os
DB = os.getenv("DB_PATH", "events.db")
def init():
 conn = sqlite3.connect(DB)
 conn.executescript("""
 CREATE TABLE IF NOT EXISTS events (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 idempotency_key TEXT NOT NULL UNIQUE,
 client_id TEXT NOT NULL,
 metric TEXT,
 amount REAL,
 timestamp TEXT,
 raw TEXT,
 received_at TEXT DEFAULT (datetime('now')),
 status TEXT DEFAULT 'processed'
 );
 CREATE INDEX IF NOT EXISTS idx_events_client ON events (client_id);
 CREATE INDEX IF NOT EXISTS idx_events_ts ON events (timestamp);
 CREATE TABLE IF NOT EXISTS rejected_events (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 raw TEXT,
 reason TEXT,
 received_at TEXT DEFAULT (datetime('now'))
 );
 """)
 conn.commit()
 conn.close()
 print(f"Database initialised: {DB}")
if __name__ == "__main__":
 init()
