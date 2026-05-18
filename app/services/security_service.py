BLOCKED_KEYWORDS = [

    "drop",
    "truncate",
    "alter",
    "exec",
    "execute",
    "attach",
    "detach",
    "pragma"

]


def validate_sql(
    sql_query: str,
    permissions: dict
):

    sql_lower = sql_query.lower().strip()

    # -----------------------------------
    # BLOCK DANGEROUS KEYWORDS
    # -----------------------------------
    for keyword in BLOCKED_KEYWORDS:

        if keyword in sql_lower:

            return {
                "allowed": False,
                "reason": f"{keyword} is permanently blocked"
            }

    # -----------------------------------
    # BLOCK MULTI STATEMENT
    # -----------------------------------
    if ";" in sql_lower:

        return {
            "allowed": False,
            "reason": "Multiple statements blocked"
        }

    query_type = sql_lower.split()[0]

    # -----------------------------------
    # DELETE CONTROL
    # -----------------------------------
    if query_type == "delete":

        if not permissions.get(
            "allow_delete",
            False
        ):

            return {
                "allowed": False,
                "reason": "DELETE permission denied"
            }

        # SAFETY
        if "where" not in sql_lower:

            return {
                "allowed": False,
                "reason": "DELETE without WHERE blocked"
            }

    # -----------------------------------
    # UPDATE CONTROL
    # -----------------------------------
    if query_type == "update":

        if not permissions.get(
            "allow_update",
            False
        ):

            return {
                "allowed": False,
                "reason": "UPDATE permission denied"
            }

        # SAFETY
        if "where" not in sql_lower:

            return {
                "allowed": False,
                "reason": "UPDATE without WHERE blocked"
            }

    return {
        "allowed": True
    }