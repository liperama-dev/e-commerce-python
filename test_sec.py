import bleach, re

def is_security_threat(value: str) -> bool:
    if not isinstance(value, str): return False
    cleaned = bleach.clean(value, tags=[], attributes={}, protocols=[], strip=True)
    if cleaned != value and '<' in value and '>' in value: return True
    sqli_pattern = re.compile(r"(?i)(\b(DROP\s+TABLE|INSERT\s+INTO|DELETE\s+FROM|UPDATE\s+.*?\s+SET|SELECT\s+.*?\s+FROM|UNION\s+ALL|UNION\s+SELECT)\b|--|;\s*$)")
    if sqli_pattern.search(value): return True
    return False

print(is_security_threat("<script>alert('xss')</script>"))
print(is_security_threat("Robert'); DROP TABLE products;--"))
