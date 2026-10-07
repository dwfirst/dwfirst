import sys
sys.path.insert(0, r"X:\05_chroma")
import chroma_store
r = chroma_store.search("память", top_k=10)
if isinstance(r, list):
    for i, item in enumerate(r):
        meta = item.get("metadata", {})
        text = item.get("text", "")[:80]
        print(i, "|", meta.get("source", "?"), "|", meta.get("origin", "?"), "|", text)
else:
    print(r)