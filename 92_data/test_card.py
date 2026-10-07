import sys
sys.path.insert(0, r"X:\01_core\modules")
import brain

# Set active project to book_iris
import json
sp = r"X:\07_router\state.json"
with open(sp, "r", encoding="utf-8-sig") as f:
    st = json.load(f)
st["project"]["active"] = "books/book_iris"
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=2)

m = brain.build_system_message()
print("=== SYSTEM MESSAGE ===")
print("length:", len(m))
print(m)
