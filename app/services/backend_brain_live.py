from app.services.db_service import execute_query

from app.services.parameter_service import (
    extract_parameters
)

from app.services.vector_service import (
    search_similar_question
)

from app.services.auth_service import (
    verify_token
)


SIMILARITY_THRESHOLD = 0.40


def backendbrain_live(

    question: str,

    token: str = None,

    role: str = None,

    authentication_required: bool = False,

    allowed_roles: list = None,

    allow_delete: bool = False,

    allow_update: bool = False,
):

    """
    Production-safe brain:
    Executes ONLY approved vector queries.
    """

    # -----------------------------------
    # EXTRACT PARAMETERS
    # -----------------------------------
    parameters = extract_parameters(
        question
    )

    print(f"\nPARAMETERS:\n{parameters}")

    # -----------------------------------
    # SEARCH VECTOR DB
    # -----------------------------------
    search_result = search_similar_question(
        question
    )

    documents = search_result.get(
        "documents",
        []
    )

    distances = search_result.get(
        "distances",
        []
    )

    metadatas = search_result.get(
        "metadatas",
        []
    )

    # -----------------------------------
    # VECTOR MATCH
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

        print(
            f"\nSIMILARITY DISTANCE:\n{similarity_distance}"
        )

        if similarity_distance < SIMILARITY_THRESHOLD:

            stored_sql = documents[0][0]

            meta = metadatas[0][0]

            # -----------------------------------
            # LOAD STORED SECURITY SETTINGS
            # -----------------------------------
            allowed_roles = meta.get(
                "allowed_roles",
                allowed_roles
            )

            authentication_required = meta.get(
                "authentication_required",
                authentication_required
            )

            allow_delete = meta.get(
                "allow_delete",
                allow_delete
            )

            allow_update = meta.get(
                "allow_update",
                allow_update
            )

            # -----------------------------------
            # JWT AUTH CHECK
            # -----------------------------------
            if authentication_required:

                # TOKEN REQUIRED
                if not token:

                    return {

                        "error": "JWT token required",

                        "code": "TOKEN_REQUIRED"
                    }

                # VERIFY JWT
                payload = verify_token(
                    token
                )

                # INVALID TOKEN
                if not payload:

                    return {

                        "error": "Invalid JWT token",

                        "code": "INVALID_TOKEN"
                    }

                # EXTRACT ROLE
                role = payload.get(
                    "role"
                )

                print(f"\nJWT ROLE:\n{role}")

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

            # -----------------------------------
            # EXECUTE SQL
            # -----------------------------------
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
    # NO VECTOR MATCH
    # -----------------------------------
    print(
        f"\nNO VECTOR MATCH for question: {question}"
    )

    return {

        "error": "This question is not currently supported.",

        "code": "NO_VECTOR_MATCH",
    }