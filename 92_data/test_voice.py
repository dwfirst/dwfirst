import sys
sys.path.insert(0, r"X:\01_core\modules")
sys.path.insert(0, r"X:\06_reflection")

import brain
import inner_voice

brain.reset()
llama, _ = brain.get_llama()

r = inner_voice.run(llama)
print("=== INNER VOICE RESULT ===")
for k, v in r.items():
    print(k, ":", v)
