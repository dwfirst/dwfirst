import sys
sys.path.insert(0, r"X:\05_chroma")
import chroma_store as chroma
res = chroma.search("как работает выжимка", top_k=3)
for r in res:
    print(r["id"], "|", round(r["distance"], 3), "|", r["text"][:80])
