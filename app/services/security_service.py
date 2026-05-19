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
    lower_sql = sql_query.lower()

    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in lower_sql:
            return {
                "allowed": False,
                "reason": f"Forbidden SQL keyword detected: '{keyword}'",
            }

    return {"allowed": True, "reason": None}