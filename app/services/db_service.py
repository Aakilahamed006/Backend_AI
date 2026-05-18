from app.database.connection import SessionLocal

from sqlalchemy import text

from app.services.correction_service import (
    correct_sql
)

from app.services.security_service import (
    validate_sql
)


def execute_query(
    sql_query: str,
    question: str,
    parameters: dict = None,
    permissions: dict = None
):

    db = SessionLocal()

    try:

        # -----------------------------------
        # SECURITY VALIDATION
        # -----------------------------------
        security_result = validate_sql(

            sql_query=sql_query,

            permissions=permissions or {}
        )

        if not security_result["allowed"]:

            return {
                "error": security_result["reason"]
            }

        # -----------------------------------
        # EXECUTE QUERY
        # -----------------------------------
        result = db.execute(

            text(sql_query),

            parameters or {}
        )

        db.commit()

        query_type = sql_query.strip().split()[0].lower()

        # -----------------------------------
        # SELECT QUERY
        # -----------------------------------
        if query_type == "select":

            rows = result.mappings().all()

            return rows

        # -----------------------------------
        # INSERT / UPDATE / DELETE
        # -----------------------------------
        return {

            "message": "Query executed successfully",

            "rows_affected": result.rowcount
        }

    except Exception as e:

        print("\nSQL ERROR:")
        print(str(e))

        # -----------------------------------
        # TRY AI CORRECTION
        # -----------------------------------
        corrected_sql = correct_sql(

            question=question,

            wrong_sql=sql_query,

            db_error=str(e)
        )

        print("\nCORRECTED SQL:")
        print(corrected_sql)

        try:

            # -----------------------------------
            # SECURITY CHECK AGAIN
            # -----------------------------------
            security_result = validate_sql(

                sql_query=corrected_sql,

                permissions=permissions or {}
            )

            if not security_result["allowed"]:

                return {
                    "error": security_result["reason"]
                }

            # -----------------------------------
            # EXECUTE CORRECTED QUERY
            # -----------------------------------
            result = db.execute(

                text(corrected_sql),

                parameters or {}
            )

            db.commit()

            query_type = corrected_sql.strip().split()[0].lower()

            # -----------------------------------
            # SELECT
            # -----------------------------------
            if query_type == "select":

                rows = result.mappings().all()

                return rows

            # -----------------------------------
            # INSERT / UPDATE / DELETE
            # -----------------------------------
            return {

                "message": "Corrected query executed successfully",

                "rows_affected": result.rowcount
            }

        except Exception as second_error:

            return {
                "error": str(second_error)
            }

    finally:

        db.close()