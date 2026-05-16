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
# STORE QUESTION + SQL
# -----------------------------
def store_query(
    question: str,
    sql_query: str
):

    embedding = embedding_model.encode(
        question
    ).tolist()

    collection.add(

        ids=[question],

        embeddings=[embedding],

        documents=[sql_query],

        metadatas=[
            {
                "question": question
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

    embedding = embedding_model.encode(
        question
    ).tolist()

    results = collection.query(

        query_embeddings=[embedding],

        n_results=1
    )

    return results