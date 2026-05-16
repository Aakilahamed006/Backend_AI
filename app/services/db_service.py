from app.database.connection import (
    SessionLocal
)

from sqlalchemy import text

from app.services.correction_service import (
    correct_sql
)


def execute_query(
    sql_query: str,
    question: str
):

    db = SessionLocal()

    try:

        result = db.execute(text(sql_query))
        db.commit()

        query_type = sql_query.strip().split()[0].lower()

        # -----------------------------
        # SELECT QUERY
        # -----------------------------
        if query_type == "select":

            rows = result.mappings().all()

            return {
                "type": "select",
                "data": rows
            }

        # -----------------------------
        # INSERT / UPDATE / DELETE
        # -----------------------------
        else:

            return {
                "type": query_type,
                "rows_affected": result.rowcount,
                "message": "Query executed successfully"
            }

    except Exception as e:

        print("\nSQL ERROR:")
        print(str(e))

        corrected_sql = correct_sql(
            question=question,
            wrong_sql=sql_query,
            db_error=str(e)
        )

        print("\nCORRECTED SQL:")
        print(corrected_sql)

        try:

            result = db.execute(text(corrected_sql))
            db.commit()

            query_type = corrected_sql.strip().split()[0].lower()

            if query_type == "select":

                rows = result.mappings().all()

                return {
                    "type": "select",
                    "data": rows,
                    "corrected": True
                }

            else:

                return {
                    "type": query_type,
                    "rows_affected": result.rowcount,
                    "corrected": True
                }

        except Exception as second_error:

            return {
                "error": str(second_error)
            }

    finally:

        db.close()