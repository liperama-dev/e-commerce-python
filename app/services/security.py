import html
import bleach


def is_security_threat(value: str) -> bool:
    """
    Check for XSS attacks.
    Rely on SQLAlchemy parameterisation for SQL injection protection.
    """
    if not isinstance(value, str):
        return False
        
    sanitised = bleach.clean(value, tags=[], attributes={}, strip=True)
    if html.unescape(sanitised) != value:
        return True

    return False
