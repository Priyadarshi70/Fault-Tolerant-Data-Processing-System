from flask import Flask, request, jsonify
import sqlite3, json, os
from normalizer import normalize
from validator import validate
app = Flask(__name__)
DB = os.getenv("DB_PATH", "events.db")
def get_db():
 conn = sqlite3.connect(DB)
 conn.row_factory = sqlite3.Row
 return conn
@app.post("/ingest")
def ingest():
 simulate_failure = request.args.get("simulate_failure", "false").lower() == "true"
 try:
 raw = request.get_json(force=True)
 except Exception:
 return jsonify({"status": "error", "message": "Invalid JSON"}), 400
 normalized = normalize(raw)
 result = validate(normalized)
 if not result.valid:
 _store_rejected(raw, result.errors)
 return jsonify({
 "status": "rejected",
 "errors": result.errors,
 }), 422
 if simulate_failure:
 return jsonify({"status": "error", "message": "Simulated DB failure"}), 500
 try:
 conn = get_db()
 conn.execute("""
 INSERT OR IGNORE INTO events
 (idempotency_key, client_id, metric, amount, timestamp, raw)
 VALUES (?, ?, ?, ?, ?, ?)
 """, (
 normalized["idempotency_key"],
 normalized["client_id"],
 normalized["metric"],
 normalized["amount"],
 normalized["timestamp"],
 json.dumps(raw),
 ))
 conn.commit()
 conn.close()
 except Exception as e:
 return jsonify({"status": "error", "message": str(e)}), 500
 return jsonify({
 "status": "ok",
 "idempotency_key": normalized["idempotency_key"],
 "warnings": result.warnings,
 }), 200
def _store_rejected(raw: dict, errors: list):
 try:
 conn = get_db()
 conn.execute(
 "INSERT INTO rejected_events (raw, reason) VALUES (?, ?)",
 (json.dumps(raw), "; ".join(errors))
 )
 conn.commit()
 conn.close()
 except Exception:
 pass # best-effort; don't let rejection storage crash the response
