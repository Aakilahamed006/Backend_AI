from app.services.ai_service import ask_ai

from app.services.db_service import (
    execute_query,
    execute_ai_query
)

from app.services.parameter_service import extract_parameters

from app.services.vector_service import (
    store_query,
    search_similar_question
)

from app.services.auth_service import verify_token


SIMILARITY_THRESHOLD = 0.40


def backend_brain(

    question: str,

    token: str = None,

    role: str = None,

    authentication_required: bool = False,

    allowed_roles: list = None,

    allow_delete: bool = False,

    allow_update: bool = False,
):

    # -----------------------------------
    # PARAMETERS
    # -----------------------------------
    parameters = extract_parameters(question)
    print(f"\nPARAMETERS:\n{parameters}")

    # -----------------------------------
    # JWT SECURITY CHECK (GLOBAL LEVEL)
    # -----------------------------------
    if authentication_required:

        if not token:

            return {
                "error": "Authentication required",
                "code": "TOKEN_MISSING"
            }

        payload = verify_token(token)

        if not payload:

            return {
                "error": "Invalid token",
                "code": "INVALID_TOKEN"
            }

        role = payload.get("role")

        print(f"\nJWT ROLE:\n{role}")

    # -----------------------------------
    # VECTOR SEARCH
    # -----------------------------------
    search_result = search_similar_question(question)

    documents = search_result.get("documents", [])
    distances = search_result.get("distances", [])
    metadatas = search_result.get("metadatas", [])

    # -----------------------------------
    # VECTOR MATCH PATH
    # -----------------------------------
    if (
        documents
        and documents[0]
        and distances
        and distances[0]
        and metadatas
        and metadatas[0]
    ):

        similarity_distance = distances[0][0]

        if similarity_distance < SIMILARITY_THRESHOLD:

            stored_sql = documents[0][0]
            meta = metadatas[0][0]

            allowed_roles = meta.get("allowed_roles", allowed_roles)
            authentication_required = meta.get("authentication_required", authentication_required)
            allow_delete = meta.get("allow_delete", allow_delete)
            allow_update = meta.get("allow_update", allow_update)

            # -----------------------------------
            # ROLE CHECK
            # -----------------------------------
            if allowed_roles:

                if role not in allowed_roles:

                    return {
                        "error": "Access denied",
                        "code": "ROLE_DENIED"
                    }

            print(f"\nREUSED SQL:\n{stored_sql}")

            return execute_query(
                sql_query=stored_sql,
                question=question,
                parameters=parameters,
                role=role,
                allow_delete=allow_delete,
                allow_update=allow_update,
                allowed_roles=allowed_roles,
                authentication_required=authentication_required,
            )

    # -----------------------------------
    # AI FALLBACK PATH (SECURED)
    # -----------------------------------
    sql_query = ask_ai(question)

    print(f"\nAI GENERATED SQL:\n{sql_query}")

    # -----------------------------------
    # SECURITY CHECK BEFORE EXECUTION
    # -----------------------------------
    if authentication_required:

        if not token:

            return {
                "error": "Authentication required",
                "code": "TOKEN_MISSING"
            }

        payload = verify_token(token)

        if not payload:

            return {
                "error": "Invalid token",
                "code": "INVALID_TOKEN"
            }

        role = payload.get("role")

    # Block dangerous SQL operations if not allowed
    lowered = sql_query.lower()

    if "delete" in lowered and not allow_delete:

        return {
            "error": "DELETE operations are not allowed",
            "code": "DELETE_BLOCKED"
        }

    if "update" in lowered and not allow_update:

        return {
            "error": "UPDATE operations are not allowed",
            "code": "UPDATE_BLOCKED"
        }

    # -----------------------------------
    # EXECUTE AI SQL
    # -----------------------------------
    result = execute_ai_query(
        sql_query=sql_query,
        question=question,
        parameters=parameters,
        allow_delete=allow_delete,
        allow_update=allow_update,
        allowed_roles=allowed_roles,
    )

    # -----------------------------------
    # STORE SUCCESSFUL QUERY
    # -----------------------------------
    if "error" not in result:

        store_query(
            question=question,
            sql_query=sql_query,
            authentication_required=authentication_required,
            allowed_roles=allowed_roles,
        )

    return result