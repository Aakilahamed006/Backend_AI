from app.database.connection import SessionLocal
from app.services.correction_service import correct_sql
from app.services.security_service import validate_sql
from sqlalchemy import text


def _validate(sql: str) -> dict | None:
    """Returns an error dict if SQL contains forbidden keywords, else None."""
    result = validate_sql(sql_query=sql)
    if not result["allowed"]:
        return {"error": result["reason"]}
    return None


def _check_permissions(
        sql_query: str,
        role: str = None,
        allow_delete: bool = False,
        allow_update: bool = False,
        allowed_roles: list = None,
        authentication_required: bool = False,
) -> dict | None:
    """
    Returns an error dict if any permission check fails, else None.

      1. authentication_required=True  → role must be provided.
      2. If authenticated and allowed_roles set → role must be in the list.
      3. DELETE / UPDATE → checked against allow_delete / allow_update flags.
      (If authentication_required=False, steps 1 & 2 are skipped entirely.)
    """
    query_type = sql_query.strip().split()[0].lower()

     #--- Step 1: Authentication ---
    if authentication_required and not role:
        return {"error": "Authentication required. No role/identity provided."}


    # --- Step 2: Role whitelist ---
    if authentication_required and role and allowed_roles:
        print("reached inside")
        if role not in allowed_roles:
            return {"error": f"Role '{role}' is not authorised to execute this query."}

    # --- Step 3: Operation flags ---
    if query_type == "delete" and not allow_delete:
        return {"error": "DELETE queries are not permitted."}

    if query_type == "update" and not allow_update:
        return {"error": "UPDATE queries are not permitted."}

    return None


def _run(db, sql: str, parameters: dict, corrected: bool = False) -> dict | list:
    """Executes a validated query and returns the result."""
    result = db.execute(text(sql), parameters)
    db.commit()

    if sql.strip().split()[0].lower() == "select":
        return result.mappings().all()

    return {
        "message": "Corrected query executed successfully" if corrected else "Query executed successfully",
        "rows_affected": result.rowcount,
    }


def execute_query(
        sql_query: str,
        question: str,
        parameters: dict = None,
        role: str = None,
        allow_delete: bool = False,
        allow_update: bool = False,
        allowed_roles: list = None,
        authentication_required: bool = False,
) -> dict | list:
    parameters = parameters or {}
    db = SessionLocal()

    try:
        # --- Permission check ---
        if (err := _check_permissions(
                sql_query=sql_query,
                role=role,
                allow_delete=allow_delete,
                allow_update=allow_update,
                allowed_roles=allowed_roles,
                authentication_required=authentication_required,
        )) is not None:
            return err

        # --- Forbidden keyword check ---
        if (err := _validate(sql_query)) is not None:
            return err

        # --- Primary execution ---
        return _run(db, sql_query, parameters)

    except Exception as primary_error:
        db.rollback()
        print(f"\nSQL ERROR:\n{primary_error}")

        # --- AI correction ---
        corrected_sql = correct_sql(
            question=question,
            wrong_sql=sql_query,
            db_error=str(primary_error),
        )
        print(f"\nCORRECTED SQL:\n{corrected_sql}")

        # --- Re-check permissions on corrected SQL ---
        if (err := _check_permissions(
                sql_query=corrected_sql,
                role=role,
                allow_delete=allow_delete,
                allow_update=allow_update,
                allowed_roles=allowed_roles,
                authentication_required=authentication_required,
        )) is not None:
            return err

        # --- Re-check forbidden keywords on corrected SQL ---
        if (err := _validate(corrected_sql)) is not None:
            return err

        # --- Retry ---
        try:
            return _run(db, corrected_sql, parameters, corrected=True)
        except Exception as second_error:
            db.rollback()
            return {"error": str(second_error)}

    finally:
        db.close()


def execute_ai_query(
        sql_query: str,
        question: str,
        parameters: dict = None,
        role: str = None,
        allow_delete: bool = False,
        allow_update: bool = False,
        allowed_roles: list = None,
        authentication_required: bool = False,
) -> dict | list:
    """
    Same as execute_query but skips authentication and role checks.
    Only enforces forbidden keyword validation and allow_delete / allow_update flags.
    Used for AI-generated queries where auth is handled upstream.
    """
    parameters = parameters or {}
    db = SessionLocal()

    try:
        # --- Forbidden keyword check only ---
        if (err := _validate(sql_query)) is not None:
            return err

        # --- Operation flags only (no auth, no role) ---
        query_type = sql_query.strip().split()[0].lower()

        if query_type == "delete" and not allow_delete:
            return {"error": "DELETE queries are not permitted."}

        if query_type == "update" and not allow_update:
            return {"error": "UPDATE queries are not permitted."}

        # --- Primary execution ---
        return _run(db, sql_query, parameters)

    except Exception as primary_error:
        db.rollback()
        print(f"\nSQL ERROR:\n{primary_error}")

        # --- AI correction ---
        corrected_sql = correct_sql(
            question=question,
            wrong_sql=sql_query,
            db_error=str(primary_error),
        )
        print(f"\nCORRECTED SQL:\n{corrected_sql}")

        # --- Re-check forbidden keywords on corrected SQL ---
        if (err := _validate(corrected_sql)) is not None:
            return err

        # --- Re-check operation flags on corrected SQL ---
        query_type = corrected_sql.strip().split()[0].lower()

        if query_type == "delete" and not allow_delete:
            return {"error": "DELETE queries are not permitted."}

        if query_type == "update" and not allow_update:
            return {"error": "UPDATE queries are not permitted."}

        # --- Retry ---
        try:
            return _run(db, corrected_sql, parameters, corrected=True)
        except Exception as second_error:
            db.rollback()
            return {"error": str(second_error)}

    finally:
        db.close()