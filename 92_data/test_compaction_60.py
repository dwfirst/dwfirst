import sys
import time

sys.path.insert(0, r"X:\01_core\modules")
sys.path.insert(0, r"X:\02_memory_fast")

import brain
import storage
import counter

brain.reset()
storage.reset_session()
llama, _ = brain.get_llama()

t0 = time.time()
triggered = 0
for i in range(60):
    r = brain.chat_one("step " + str(i), max_tokens=30)
    if r.get("compaction", {}).get("triggered"):
        triggered += 1
        stats = r["compaction"].get("stats", {})
        w = storage.read_window()
        print("  >>> COMPACTION at step", i + 1, "| window msgs:", len(w), "| tokens:", counter.count_window(llama, w), "| old:", stats.get("old_messages"), "| fresh:", stats.get("fresh_messages"))

s = storage.stats()
w = storage.read_window()
print("=== DONE ===")
print("session msgs:", s["session_messages"])
print("window msgs:", s["window_messages"])
print("window tokens:", counter.count_window(llama, w))
print("compactions triggered:", triggered)
print("elapsed:", round(time.time() - t0, 1), "sec")
