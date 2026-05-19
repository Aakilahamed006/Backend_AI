import re
import uuid
import chromadb
from sentence_transformers import SentenceTransformer


# -----------------------------
# LOAD EMBEDDING MODEL
# -----------------------------
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


# -----------------------------
# CREATE CHROMA CLIENT
# -----------------------------
client = chromadb.PersistentClient(path="./vector_db")


# -----------------------------
# CREATE COLLECTION
# -----------------------------
collection = client.get_or_create_collection(name="sql_memory")


# -----------------------------
# NORMALIZE QUESTION
# -----------------------------
def normalize_question(question: str) -> str:
    return re.sub(r"\[.*?\]", "", question).strip().lower()


# -----------------------------
# STORE QUESTION + SQL
# -----------------------------
def store_query(
    question: str,
    sql_query: str,
    authentication_required: bool = False,
    allowed_roles: list = None,
) -> None:

    normalized_question = normalize_question(question)

    # --- Duplicate check ---
    existing = collection.query(
        query_embeddings=[embedding_model.encode(normalized_question).tolist()],
        n_results=1,
    )
    if (
        existing["documents"]
        and existing["documents"][0]
        and existing["distances"]
        and existing["distances"][0]
        and existing["distances"][0][0] < 0.01
    ):
        print("Duplicate question detected — skipping store.")
        return

    embedding = embedding_model.encode(normalized_question).tolist()

    # ✅ Convert list to comma-separated string — ChromaDB only supports scalar metadata values
    allowed_roles_str = ",".join(allowed_roles) if allowed_roles else ""

    collection.add(
        ids=[str(uuid.uuid4())],
        embeddings=[embedding],
        documents=[sql_query],
        metadatas=[
            {
                "question": normalized_question,
                "authentication_required": authentication_required,
                "allowed_roles": allowed_roles_str,   # ✅ stored as "admin,user" not ["admin","user"]
            }
        ],
    )
    print(f"Stored in vector DB — allowed_roles: '{allowed_roles_str}'")


# -----------------------------
# SEARCH SIMILAR QUESTION
# -----------------------------
def search_similar_question(question: str) -> dict:

    normalized_question = normalize_question(question)
    embedding = embedding_model.encode(normalized_question).tolist()

    results = collection.query(
        query_embeddings=[embedding],
        n_results=1,
        include=["documents", "distances", "metadatas"],  # ✅ explicit — guarantees metadatas is returned
    )

    # ✅ Parse allowed_roles back from "admin,user" → ["admin", "user"]
    if results["metadatas"] and results["metadatas"][0]:
        for meta in results["metadatas"][0]:
            raw = meta.get("allowed_roles", "")
            meta["allowed_roles"] = [r for r in raw.split(",") if r]
    print("DOCUMENTS:", results["documents"])
    print("METADATAS:", results["metadatas"])
    return results