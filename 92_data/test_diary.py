import sys
sys.path.insert(0, r"X:\01_core\modules")
sys.path.insert(0, r"X:\06_reflection")

import brain
import diary

brain.reset()
llama, _ = brain.get_llama()

r = diary.run(llama)
print("=== DIARY RESULT ===")
for k, v in r.items():
    print(k, ":", v)
