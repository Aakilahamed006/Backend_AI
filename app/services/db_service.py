from app.database.connection import SessionLocal

from sqlalchemy import text

from app.services.correction_service import correct_sql


def execute_query(
    sql_query: str,
    question: str,
    parameters: dict = None
):

    db = SessionLocal()

    try:

        result = db.execute(
            text(sql_query),
            parameters or {}
        )

        db.commit()

        query_type = sql_query.strip().split()[0].lower()

        # -----------------------------
        # SELECT QUERY
        # -----------------------------
        if query_type == "select":

            rows = result.mappings().all()

            return rows

        # -----------------------------
        # INSERT / UPDATE / DELETE
        # -----------------------------
        return {
            "message": "Query executed successfully",
            "rows_affected": result.rowcount
        }

    except Exception as e:

        return {
            "error": str(e)
        }

    finally:

        db.close()