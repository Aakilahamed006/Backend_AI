from app.services.ai_service import ask_ai

from app.services.db_service import execute_query

from app.services.vector_service import (
    store_query,
    search_similar_question
)


def backend_brain(question: str):

    # -----------------------------------
    # STEP 1: SEARCH VECTOR DATABASE
    # -----------------------------------
    search_result = search_similar_question(
        question
    )

    documents = search_result.get(
        "documents",
        []
    )

    # -----------------------------------
    # STEP 2: IF SIMILAR QUESTION EXISTS
    # -----------------------------------
    if documents and documents[0]:

        print("\nFOUND IN VECTOR DATABASE")

        stored_sql = documents[0][0]

        print("REUSED SQL:")
        print(stored_sql)

        return execute_query(
            sql_query=stored_sql,
            question=question
        )

    # -----------------------------------
    # STEP 3: OTHERWISE USE AI
    # -----------------------------------
    print("\nNOT FOUND IN VECTOR DATABASE")

    sql_query = ask_ai(question)

    # -----------------------------------
    # STEP 4: EXECUTE SQL
    # -----------------------------------
    result = execute_query(
        sql_query=sql_query,
        question=question
    )

    # -----------------------------------
    # STEP 5: STORE SUCCESSFUL QUERY
    # -----------------------------------
    if isinstance(result, list):

        store_query(
            question=question,
            sql_query=sql_query
        )

    return result