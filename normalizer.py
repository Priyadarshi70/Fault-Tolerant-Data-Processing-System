import hashlib, json
from datetime import datetime, timezone
from typing import Any, Optional
# ■■ Field alias map (extend per client as needed) ■■■■■■■■■■■■■■■■■■■■■■■■■■
FIELD_ALIASES: dict[str, list[str]] = {
 "metric": ["metric", "event_type", "name", "type"],
 "amount": ["amount", "value", "count", "qty", "quantity"],
 "timestamp": ["timestamp", "ts", "event_time", "created_at", "date"],
}
def _resolve_field(payload: dict, canonical: str) -> Optional[Any]:
 """Return the first matching alias value, or None."""
 for alias in FIELD_ALIASES.get(canonical, [canonical]):
 if alias in payload:
 return payload[alias]
 return None
def _parse_amount(raw: Any) -> Optional[float]:
 try:
 return float(str(raw).replace(",", "").strip())
 except (TypeError, ValueError):
 return None
def _parse_timestamp(raw: Any) -> Optional[str]:
 if raw is None:
 return None
 formats = [
 "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S",
 "%Y/%m/%d", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y",
 ]
 raw_str = str(raw).strip()
 for fmt in formats:
 try:
 dt = datetime.strptime(raw_str, fmt).replace(tzinfo=timezone.utc)
 return dt.isoformat().replace("+00:00", "Z")
 except ValueError:
 continue
 return None # malformed — caller decides what to do
def normalize(raw_event: dict) -> dict:
 """
 Convert a raw incoming event to the canonical internal format.
 Returns a dict; sets fields to None when unresolvable.
 """
 source = raw_event.get("source") or raw_event.get("client_id", "unknown")
 payload = raw_event.get("payload", raw_event) # flat or nested
 metric = _resolve_field(payload, "metric")
 raw_amt = _resolve_field(payload, "amount")
 raw_ts = _resolve_field(payload, "timestamp")
 normalized = {
 "client_id": str(source),
 "metric": str(metric) if metric is not None else None,
 "amount": _parse_amount(raw_amt),
 "timestamp": _parse_timestamp(raw_ts),
 "raw": raw_event, # keep original for audit / replay
 }
 # Stable idempotency key — used for deduplication (see section 3)
 key_material = json.dumps(
 {k: normalized[k] for k in ("client_id", "metric", "amount", "timestamp")},
 sort_keys=True
 )
 normalized["idempotency_key"] = hashlib.sha256(
 key_material.encode()
 ).hexdigest()
 return normalized
