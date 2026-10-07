import sys
sys.path.insert(0, r"X:\01_core\modules")
sys.path.insert(0, r"X:\06_reflection")

import brain
import dream

brain.reset()
llama, _ = brain.get_llama()

r = dream.run(llama, sample_size=12)
print("=== DREAM RESULT ===")
for k, v in r.items():
    print(k, ":", v)
