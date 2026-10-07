import sys
sys.path.insert(0, r"X:\05_chroma")
import module as chroma
import chromadb

client = chroma._get_client()
try:
    client.delete_collection("iris_memory")
    print("old collection deleted")
except Exception as e:
    print("delete:", e)

chroma._COLLECTION = None
print("count after reset:", chroma.count())

chroma.add("test_1", "The archive is permanent and never deleted.", metadata={"role": "user"})
chroma.add("test_2", "Sliding window compaction summarizes old messages.", metadata={"role": "assistant"})
chroma.add("test_3", "The model is just a voice, memory is separate.", metadata={"role": "user"})
print("count after add:", chroma.count())

res = chroma.search("archive permanent forever", top_k=2)
print("--- SEARCH ---")
for r in res:
    print(r["id"], "|", round(r["distance"], 3), "|", r["text"][:60])

print("--- STATS ---")
print(chroma.stats())
