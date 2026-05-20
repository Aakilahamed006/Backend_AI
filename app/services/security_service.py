FORBIDDEN_KEYWORDS = [
    "drop",
    "truncate",
    "alter",
    "create database",
    "drop database",
]

def validate_sql(sql_query: str) -> dict:
    """
    Checks for forbidden SQL keywords.
    Always returns {"allowed": bool, "reason": str | None}
    """

    # 1. Handle None or empty input
    if not sql_query:
        return {
            "allowed": False,
            "reason": "SQL query is empty or None"
        }

    # 2. Ensure it's a string
    if not isinstance(sql_query, str):
        return {
            "allowed": False,
            "reason": f"Invalid SQL type: {type(sql_query).__name__}"
        }

    lower_sql = sql_query.lower()

    # 3. Check forbidden keywords
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in lower_sql:
            return {
                "allowed": False,
                "reason": f"Forbidden SQL keyword detected: '{keyword}'",
            }

    return {"allowed": True, "reason": None}