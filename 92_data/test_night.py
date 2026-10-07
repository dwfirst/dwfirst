import sys
sys.path.insert(0, r"X:\01_core\modules")
sys.path.insert(0, r"X:\06_reflection")

import brain
import night_mode

brain.reset()
llama, _ = brain.get_llama()

r = night_mode.run(llama, stages=["diary"])
print("=== NIGHT MODE RESULT ===")
print("ok:", r["ok"])
print("stages_run:", r["stages_run"])
print("stages_ok:", r["stages_ok"])
print("elapsed:", r["elapsed"])
print("summary:", r["summary"])
d = r["results"].get("diary", {})
print("--- diary ---")
for k, v in d.items():
    if k != "summary_preview":
        print(" ", k, ":", v)
