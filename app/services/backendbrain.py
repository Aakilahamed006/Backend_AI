from app.services.ai_service import ask_ai

from app.services.db_service import execute_query

from app.services.parameter_service import (
    extract_parameters
)

from app.services.vector_service import (
    store_query,
    search_similar_question
)


SIMILARITY_THRESHOLD = 0.40


def backend_brain(
    question: str,
    permissions: dict
):

    # -----------------------------------
    # EXTRACT PARAMETERS
    # -----------------------------------
    parameters = extract_parameters(question)

    print("\nPARAMETERS:")
    print(parameters)

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

    # -----------------------------------
    # VECTOR MATCH
    # -----------------------------------
    if (
        documents
        and documents[0]
        and distances
        and distances[0]
    ):

        similarity_distance = distances[0][0]

        print("\nSIMILARITY DISTANCE:")
        print(similarity_distance)

        if similarity_distance < SIMILARITY_THRESHOLD:

            stored_sql = documents[0][0]

            print("\nREUSED SQL:")
            print(stored_sql)

            return execute_query(

                sql_query=stored_sql,

                question=question,

                parameters=parameters,

                permissions=permissions
            )

    # -----------------------------------
    # OTHERWISE USE AI
    # -----------------------------------
    sql_query = ask_ai(question)

    print("\nAI GENERATED SQL:")
    print(sql_query)

    # -----------------------------------
    # EXECUTE SQL
    # -----------------------------------
    result = execute_query(

        sql_query=sql_query,

        question=question,

        parameters=parameters,

        permissions=permissions
    )

    # -----------------------------------
    # STORE SUCCESSFUL TEMPLATE
    # -----------------------------------
    if "error" not in result:

        store_query(

            question=question,

            sql_query=sql_query
        )

    return result