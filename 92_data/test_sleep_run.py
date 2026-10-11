import sys
import time
sys.path.insert(0, r"X:\06_reflection")
sys.path.insert(0, r"X:\03_memory_working")
sys.path.insert(0, r"X:\01_core\modules")
import brain
import sleep

print("Loading model...")
llama, _ = brain.get_llama()
print("Model loaded. Running sleep...")

t0 = time.time()
r = sleep.run(llama, days=7, max_groups=4)
elapsed = round(time.time() - t0, 1)

print()
print("=== SLEEP RESULT ===")
print("ok:", r.get("ok"))
print("facts_input:", r.get("facts_input"))
print("groups:", r.get("groups"))
print("consolidated:", r.get("consolidated"))
print("archived:", r.get("archived"))
print("elapsed:", r.get("elapsed"))
print()
print("preview:")
for p in r.get("preview", []):
    print(f"  [{p['theme']}] ({p['source_count']} facts)")
    print(f"    {p['preview'][:200]}")
print()
print(f"Total wall time: {elapsed}s")