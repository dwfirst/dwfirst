"""stress_test.py - 100 messages through brain.chat_one()."""
import sys
import time

sys.path.insert(0, r"X:\01_core\modules")
sys.path.insert(0, r"X:\02_memory_fast")

import brain
import storage
import counter
import compaction

# Reduce t_max for stress test (do not modify config.json)
compaction.T_MAX = 2000

brain.reset()
storage.reset_session()

llama, _ = brain.get_llama()

phrases = [
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa",
]

t0 = time.time()
for i in range(100):
    phrase = phrases[i % len(phrases)] + " " + str(i)
    r = brain.chat_one(phrase, max_tokens=30)

    if (i + 1) % 10 == 0:
        s = storage.stats()
        w = storage.read_window()
        w_tokens = counter.count_window(llama, w)
        print("--- step", i + 1, "---")
        print("  session msgs:", s["session_messages"])
        print("  window msgs:", s["window_messages"], "| tokens:", w_tokens)
        print("  compaction triggered:", r.get("compaction", {}).get("triggered", False))
        print("  tps:", r["tps"])

elapsed = time.time() - t0
print("=== DONE ===")
print("total time:", round(elapsed, 1), "sec")
print("avg per msg:", round(elapsed / 100, 2), "sec")
s = storage.stats()
print("final session msgs:", s["session_messages"])
print("final window msgs:", s["window_messages"])
w = storage.read_window()
print("final window tokens:", counter.count_window(llama, w))
print("archive size:", s.get("archive", {}).get("total", "?"))
