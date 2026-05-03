# Fault-Tolerant-Data-Processing-System

What assumptions did you make?
Events always arrive as JSON. SQLite is acceptable for a single-process prototype (swap for Postgres in
production). The idempotency key is derived from (client_id, metric, amount, timestamp); two events that share
all four values are considered identical. Timestamps that cannot be parsed are treated as required fields and the
event is rejected. No authentication layer is implemented per the spec.
How does your system prevent double counting?
A SHA-256 hash of the four canonical fields becomes the idempotency_key, stored with a UNIQUE constraint.
Every INSERT uses ON CONFLICT DO NOTHING / INSERT OR IGNORE, so retried identical events are
silently discarded at the database level without affecting aggregates. The HTTP response is identical for
first-insert and duplicate, so clients observe no difference.
What happens if the database fails mid-request?
The Flask handler wraps the INSERT in a try/except and returns HTTP 500. The event is not counted. On retry
the client re-submits; the idempotency key guarantees the write is a safe no-op if the first attempt partially
succeeded. Rejected events are stored in a separate rejected_events table on a best-effort basis.
What would break first at scale?
SQLite's single-writer lock becomes the bottleneck immediately under concurrent load. Replacing it with
Postgres and a connection pool solves that. Next, a single Flask process saturates CPU on normalisation; a
queue (Redis + Celery / Kafka) would decouple ingestion from processing. The SHA-256 dedup key also widens
collision risk if clients send structurally identical but semantically distinct events — a client-supplied nonce field
would tighten this.
Project File Structure
/
■■■ app.py # Flask API — ingestion + query endpoints
■■■ normalizer.py # Raw → canonical conversion + idempotency key
■■■ validator.py # Required-field + type validation
■■■ idempotency.py # Dedup strategy notes + SQL constants
■■■ init_db.py # One-time DB schema setup
■■■ index.html # Frontend (serve via Flask static or open directly)
■■■ events.db # SQLite file (auto-created on first run)
■■■ README.md # This document
Quick Start
pip install flask
python init_db.py
python app.py
# Open index.html in a browser (same origin as Flask on :5000)
Evaluation Criteria
We are evaluating: System thinking, Data modeling, Failure handling, and Ability to explain decisions. We are NOT
evaluating speed, UI polish, or framework knowledge.
Optional extension: If time permits, consider schema evolution — old data must remain queryable as formats
change. Strategy: keep the raw JSON blob intact in the events table and re-normalise on read using a versioned
normalizer registry.
