"""module.py - ChromaDB wrapper for IRIS with local embedding model.

Persistent vector storage. Collection: iris_memory.
Embedding model lives in X:/05_chroma/models (portable, not on C:).

API:
  add(doc_id, text, metadata) -> None
  add_batch(items) -> int
  search(query, top_k) -> list of dicts
  count() -> int
  reset() -> None
  stats() -> dict
"""
import os
from pathlib import Path

X = "X:" + os.sep
CHROMA_DIR = os.path.join(X, "05_chroma")
DB_DIR = os.path.join(CHROMA_DIR, "db")
MODELS_DIR = os.path.join(CHROMA_DIR, "models", "onnx_models", "all-MiniLM-L6-v2")
COLLECTION_NAME = "iris_memory"

_CLIENT = None
_COLLECTION = None


def _ensure_dir():
    if not os.path.isdir(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)


def _get_embedding_function():
    """Returns ONNXMiniLM_L6_V2 with DOWNLOAD_PATH pointing to X:."""
    from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

    class LocalONNX(ONNXMiniLM_L6_V2):
        def __init__(self, preferred_providers=None):
            super().__init__(preferred_providers=preferred_providers)
            self.DOWNLOAD_PATH = Path(MODELS_DIR)

    return LocalONNX()


def _get_client():
    global _CLIENT
    if _CLIENT is None:
        import chromadb
        _ensure_dir()
        _CLIENT = chromadb.PersistentClient(path=DB_DIR)
    return _CLIENT


def get_collection():
    global _COLLECTION
    if _COLLECTION is None:
        client = _get_client()
        ef = _get_embedding_function()
        _COLLECTION = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=ef,
        )
    return _COLLECTION


def add(doc_id, text, metadata=None):
    if not text:
        return None
    col = get_collection()
    col.add(ids=[doc_id], documents=[text], metadatas=[metadata if metadata else {"source": "unknown"}])
    return doc_id


def add_batch(items):
    if not items:
        return 0
    col = get_collection()
    ids = []
    docs = []
    metas = []
    for it in items:
        if not it.get("text"):
            continue
        ids.append(it["id"])
        docs.append(it["text"])
        metas.append(it.get("metadata") or {})
    if not ids:
        return 0
    metas = [m if m else {"source": "unknown"} for m in metas]
    col.add(ids=ids, documents=docs, metadatas=metas)
    return len(ids)


def search(query, top_k=5, origin_filter=None, confidence_filter=None):
    """
    Semantic search with optional filters.

    origin_filter: None | str | list of str.
        Example: "user", ["user", "assistant"]
    confidence_filter: None | str | list of str.
        Example: "high", ["high", "medium"]
    """
    if not query:
        return []
    col = get_collection()

    where = None
    conditions = []

    if origin_filter is not None:
        if isinstance(origin_filter, list):
            conditions.append({"origin": {"$in": origin_filter}})
        else:
            conditions.append({"origin": origin_filter})

    if confidence_filter is not None:
        if isinstance(confidence_filter, list):
            conditions.append({"confidence": {"$in": confidence_filter}})
        else:
            conditions.append({"confidence": confidence_filter})

    if len(conditions) == 1:
        where = conditions[0]
    elif len(conditions) > 1:
        where = {"$and": conditions}

    try:
        if where is None:
            res = col.query(query_texts=[query], n_results=top_k)
        else:
            res = col.query(query_texts=[query], n_results=top_k, where=where)
    except Exception as e:
        return [{"error": str(e)}]

    out = []
    if not res or not res.get("ids") or not res["ids"][0]:
        return out
    ids = res["ids"][0]
    docs = res["documents"][0] if res.get("documents") else [""] * len(ids)
    metas = res["metadatas"][0] if res.get("metadatas") else [{}] * len(ids)
    dists = res["distances"][0] if res.get("distances") else [0.0] * len(ids)
    for i, doc_id in enumerate(ids):
        out.append({
            "id": doc_id,
            "text": docs[i],
            "metadata": metas[i] or {},
            "distance": dists[i],
        })
    return out


def count():
    col = get_collection()
    try:
        return col.count()
    except Exception:
        return 0


def reset():
    global _COLLECTION
    client = _get_client()
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
    _COLLECTION = None


def stats():
    return {
        "collection": COLLECTION_NAME,
        "db_path": DB_DIR,
        "models_path": MODELS_DIR,
        "count": count(),
    }


if __name__ == "__main__":
    print("chroma module. stats:", stats())
