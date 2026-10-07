import sys
sys.path.insert(0, r"X:\05_chroma")
import chroma_store as chroma

col = chroma.get_collection()
before = chroma.count()
print("before:", before)

# Delete known test ids
try:
    col.delete(ids=["test_1", "test_2", "test_3"])
    print("deleted test_1, test_2, test_3")
except Exception as e:
    print("delete error:", e)

after = chroma.count()
print("after:", after)
