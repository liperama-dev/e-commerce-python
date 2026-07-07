import html
import bleach


def is_security_threat(value: str) -> bool:
    """
    Check for XSS attacks.
    SQLi checks were removed in Phase 5 because SQLAlchemy parameterisation
    provides robust protection without false positives.
    """
    if not isinstance(value, str):
        return False
        
    sanitised = bleach.clean(value, tags=[], attributes={}, strip=True)
    if html.unescape(sanitised) != value:
        return True

    return False
