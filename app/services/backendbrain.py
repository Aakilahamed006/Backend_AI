from app.services.ai_service import ask_ai
from app.services.db_service import execute_query, execute_ai_query
from app.services.parameter_service import extract_parameters
from app.services.vector_service import store_query, search_similar_question


SIMILARITY_THRESHOLD = 0.40


def backend_brain(
    question: str,
    role: str = None,
    authentication_required: bool = False,
    allowed_roles: list = None,
    allow_delete: bool = False,
    allow_update: bool = False,
):
    # --- Extract parameters ---
    parameters = extract_parameters(question)
    print(f"\nPARAMETERS:\n{parameters}")

    # --- Search vector DB ---
    search_result = search_similar_question(question)

    documents = search_result.get("documents", [])
    distances = search_result.get("distances", [])
    metadatas = search_result.get("metadatas", [])  # ✅ Fix 1: was reading from undefined `results`

    # --- Vector match ---
    if (
        documents
        and documents[0]
        and distances
        and distances[0]
        and metadatas          # ✅ Fix 2: also guard metadatas before indexing
        and metadatas[0]
    ):
        similarity_distance = distances[0][0]
        print(f"\nSIMILARITY DISTANCE:\n{similarity_distance}")

        if similarity_distance < SIMILARITY_THRESHOLD:
            stored_sql = documents[0][0]
            meta = metadatas[0][0]                                     # ✅ Fix 1 cont.

            # Pull overrides from stored metadata; fall back to caller's values
            allowed_roles = meta.get("allowed_roles", allowed_roles)
            print(f"\nALLOWED ROLES:\n{allowed_roles}")
            authentication_required = meta.get("authentication_required", authentication_required)
            print(f"\nAUTHENTICATION REQUIRED:\n{authentication_required}")
            print(f"\nRole:\n{role}")
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

    # --- AI fallback ---
    sql_query = ask_ai(question)
    print(f"\nAI GENERATED SQL:\n{sql_query}")

    # --- Execute ---
    result = execute_ai_query(
        sql_query=sql_query,
        question=question,
        parameters=parameters,

        allow_delete=allow_delete,
        allow_update=allow_update,
        allowed_roles=allowed_roles,

    )

    # --- Store successful query as template ---
    if "error" not in result:
        store_query(
            question=question,
            sql_query=sql_query,
            authentication_required=authentication_required,
            allowed_roles=allowed_roles,
        )


    return result