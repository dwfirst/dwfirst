import sys
sys.path.insert(0, r"X:\01_core\modules")

import brain

brain.reset()
brain.storage.reset_session()

r = brain.chat_one("How does sliding window compaction work in IRIS?", max_tokens=200)
print("=== ANSWER ===")
print(r["text"])
print("=== BUDGET ===")
b = r["budget"]
print("role_tokens:", b["role_tokens"], "/ cap:", b["role_cap"])
print("retrieval:", b["retrieval"])
print("window_cap:", b["window_cap"])
print("reserve:", b["reserve"])
print("tps:", r["tps"])
