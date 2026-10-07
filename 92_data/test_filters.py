import sys
sys.path.insert(0, r"X:\05_chroma")
import chroma_store as chroma

print("--- all ---")
res = chroma.search("memory", top_k=5)
for r in res:
    print(r["id"], "|", r.get("metadata", {}))

print("--- origin=user ---")
res = chroma.search("memory", top_k=5, origin_filter="user")
for r in res:
    print(r["id"], "|", r.get("metadata", {}).get("origin"))

print("--- origin=assistant (should be empty now) ---")
res = chroma.search("memory", top_k=5, origin_filter="assistant")
print("count:", len(res))

print("--- confidence=high ---")
res = chroma.search("memory", top_k=5, confidence_filter="high")
print("count:", len(res))
