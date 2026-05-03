from dataclasses import dataclass, field
from typing import Optional
@dataclass
class ValidationResult:
 valid: bool
 errors: list[str] = field(default_factory=list)
 warnings: list[str] = field(default_factory=list)
REQUIRED_FIELDS = ["client_id", "metric", "timestamp"]
def validate(normalized: dict) -> ValidationResult:
 errors, warnings = [], []
 for f in REQUIRED_FIELDS:
 if normalized.get(f) is None:
 errors.append(f"Missing required field: {f}")
 if normalized.get("amount") is None:
 warnings.append("amount is None — will be stored as NULL")
 if normalized.get("timestamp") is None:
 errors.append("timestamp could not be parsed")
 return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
