import re
import chromadb

from sentence_transformers import SentenceTransformer


# -----------------------------
# LOAD EMBEDDING MODEL
# -----------------------------
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# -----------------------------
# CREATE CHROMA CLIENT
# -----------------------------
client = chromadb.PersistentClient(
    path="./vector_db"
)


# -----------------------------
# CREATE COLLECTION
# -----------------------------
collection = client.get_or_create_collection(
    name="sql_memory"
)


# -----------------------------
# NORMALIZE QUESTION
# -----------------------------
def normalize_question(question: str):

    return re.sub(
        r"\[.*?\]",
        "",
        question
    ).strip()


# -----------------------------
# STORE QUESTION + SQL
# -----------------------------
def store_query(
    question: str,
    sql_query: str
):

    # REMOVE VALUES INSIDE []
    normalized_question = normalize_question(
        question
    )

    embedding = embedding_model.encode(
        normalized_question
    ).tolist()

    collection.add(

        ids=[normalized_question],

        embeddings=[embedding],

        documents=[sql_query],

        metadatas=[
            {
                "question": normalized_question
            }
        ]
    )

    print("Stored in vector DB")


# -----------------------------
# SEARCH SIMILAR QUESTIONS
# -----------------------------
def search_similar_question(
    question: str
):

    # REMOVE VALUES INSIDE []
    normalized_question = normalize_question(
        question
    )

    embedding = embedding_model.encode(
        normalized_question
    ).tolist()

    results = collection.query(

        query_embeddings=[embedding],

        n_results=1
    )

    return results