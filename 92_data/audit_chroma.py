import sys
sys.path.insert(0, r"X:\05_chroma")
import chroma_store as chroma

col = chroma.get_collection()
res = col.get(limit=10)
print("total:", chroma.count())
print("--- ids ---")
for i in res.get("ids", []):
    print(i)
print("--- metadatas ---")
for m in res.get("metadatas", []):
    print(m)
