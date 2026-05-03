"""
Idempotency strategy
====================
1. normalizer.py produces a SHA-256 idempotency_key from
 (client_id, metric, amount, timestamp).
2. The DB table has UNIQUE(idempotency_key).
3. On insert we use INSERT OR IGNORE (SQLite) / INSERT … ON CONFLICT DO NOTHING (Postgres).
4. The API response is identical on first insert and on duplicates,
 so retrying clients observe the same behaviour.
Trade-offs
----------
- Two events with identical fields but different semantics collapse into one.
 Mitigation: ask clients to include a nonce/sequence if they need true uniqueness.
- If a timestamp cannot be parsed it defaults to None, widening the collision window.
 Mitigation: treat missing-timestamp events as always-insert (lower dedup guarantee).
"""
INSERT_SQL_SQLITE = """
 INSERT OR IGNORE INTO events
 (idempotency_key, client_id, metric, amount, timestamp, raw)
 VALUES (?, ?, ?, ?, ?, ?)
"""
INSERT_SQL_POSTGRES = """
 INSERT INTO events
 (idempotency_key, client_id, metric, amount, timestamp, raw)
 VALUES (%s, %s, %s, %s, %s, %s)
 ON CONFLICT (idempotency_key) DO NOTHING
