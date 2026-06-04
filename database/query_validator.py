import re

# List of forbidden modification keywords
FORBIDDEN_KEYWORDS = [
    "insert", "update", "delete", "drop", "alter", 
    "truncate", "create", "replace", "rename", "grant", "revoke"
]

def is_read_only_query(sql: str) -> bool:
    """
    Checks if a SQL query contains only read-only statements (SELECT, SHOW, etc.)
    and does not contain any data-modifying commands.
    
    Args:
        sql (str): The SQL query string to validate.
        
    Returns:
        bool: True if query is read-only, False otherwise.
    """
    # Remove block comments /* ... */ to prevent bypassing keywords check inside comments
    cleaned_sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    
    # Remove line comments starting with -- or #
    cleaned_sql = re.sub(r'(--|#).*?\n', '\n', cleaned_sql)
    
    cleaned_sql = cleaned_sql.strip()
    
    if not cleaned_sql:
        return True
        
    # Extract the first word (ignoring leading whitespace and punctuation)
    first_word_match = re.match(r'^\s*([a-zA-Z]+)', cleaned_sql)
    if not first_word_match:
        return False
        
    first_word = first_word_match.group(1).upper()
    
    # Allowed read-only starting keywords
    ALLOWED_START_KEYWORDS = {"SELECT", "WITH", "SHOW", "DESCRIBE", "EXPLAIN"}
    if first_word not in ALLOWED_START_KEYWORDS:
        return False
        
    # Check for any forbidden keywords anywhere in the query (with word boundaries)
    for kw in FORBIDDEN_KEYWORDS:
        pattern = rf'\b{kw}\b'
        if re.search(pattern, cleaned_sql, re.IGNORECASE):
            return False
            
    return True
