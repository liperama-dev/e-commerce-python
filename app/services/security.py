import re

import bleach


def is_xss_threat(value: str) -> bool:
    """
    Return True if *value* contains active HTML/XSS payloads.

    NOTE: SQL-injection defence is intentionally left to SQLAlchemy's
    built-in query parameterisation — no regex needed here.
    The SQLi regex that existed in the original codebase has been removed
    in Phase 5 (security hardening).  This function is kept for XSS only.
    """
    if not isinstance(value, str):
        return False
    cleaned = bleach.clean(value, tags=[], attributes={}, protocols=[], strip=True)
    return cleaned != value and "<" in value and ">" in value


# ---------------------------------------------------------------------------
# Phase 1 legacy — kept for backward compat with csv_import.py
# Will be removed when Phase 5 drops the SQLi regex entirely.
# ---------------------------------------------------------------------------
def is_security_threat(value: str) -> bool:
    """Combined XSS + SQLi check (Phase 1 behaviour, to be simplified in Phase 5)."""
    if not isinstance(value, str):
        return False

    # XSS check
    if is_xss_threat(value):
        return True

    # Rudimentary SQLi keyword check — will be removed in Phase 5
    sqli_pattern = re.compile(
        r"(?i)(\b(DROP\s+TABLE|INSERT\s+INTO|DELETE\s+FROM|UPDATE\s+.*?\s+SET|"
        r"SELECT\s+.*?\s+FROM|UNION\s+ALL|UNION\s+SELECT)\b|--|;\s*$)"
    )
    return bool(sqli_pattern.search(value))
