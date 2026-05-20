from app.services.db_service import execute_query
from app.services.parameter_service import extract_parameters
from app.services.vector_service import search_similar_question


SIMILARITY_THRESHOLD = 0.40


def backendbrain_live(
    question: str,
    role: str = None,
    authentication_required: bool = False,
    allowed_roles: list = None,
    allow_delete: bool = False,
    allow_update: bool = False,
):
    """
    Production-safe brain: only executes pre-vetted SQL from the vector store.
    No AI fallback — unrecognised questions are rejected outright.
    """

    # --- Extract parameters ---
    parameters = extract_parameters(question)
    print(f"\nPARAMETERS:\n{parameters}")

    # --- Search vector DB ---
    search_result = search_similar_question(question)

    documents = search_result.get("documents", [])
    distances = search_result.get("distances", [])
    metadatas = search_result.get("metadatas", [])

    # --- Vector match only ---
    if (
        documents
        and documents[0]
        and distances
        and distances[0]
        and metadatas
        and metadatas[0]
    ):
        similarity_distance = distances[0][0]
        print(f"\nSIMILARITY DISTANCE:\n{similarity_distance}")

        if similarity_distance < SIMILARITY_THRESHOLD:
            stored_sql = documents[0][0]
            meta = metadatas[0][0]

            # Pull overrides from stored metadata; fall back to caller's values
            allowed_roles = meta.get("allowed_roles", allowed_roles)
            print(f"\nALLOWED ROLES:\n{allowed_roles}")
            authentication_required = meta.get("authentication_required", authentication_required)
            print(f"\nAUTHENTICATION REQUIRED:\n{authentication_required}")
            print(f"\nROLE:\n{role}")
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

    # --- No match: reject safely (no AI, no guessing) ---
    print(f"\nNO VECTOR MATCH for question: {question}")
    return {
        "error": "This question is not currently supported. Please contact your administrator.",
        "code": "NO_VECTOR_MATCH",
    }