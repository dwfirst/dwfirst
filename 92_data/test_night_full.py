import sys
import time

sys.path.insert(0, r"X:\01_core\modules")
sys.path.insert(0, r"X:\06_reflection")

import brain
import night_mode

brain.reset()
llama, _ = brain.get_llama()

print("=== NIGHT MODE START ===")
print("stages: diary -> inner_voice -> dream")

r = night_mode.run(llama)
print()
print("=== RESULT ===")
print("ok:", r["ok"])
print("stages_run:", r["stages_run"])
print("stages_ok:", r["stages_ok"])
print("elapsed:", r["elapsed"], "sec")
print("summary:", r["summary"])
print()
for stage in ["diary", "inner_voice", "dream"]:
    s = r["results"].get(stage, {})
    print("--- " + stage + " ---")
    print("  ok:", s.get("ok"))
    print("  stage_seconds:", s.get("stage_seconds"))
    if stage == "diary":
        print("  messages:", s.get("messages"))
        print("  chunks:", s.get("chunks"))
        print("  summary_tokens:", s.get("summary_tokens"))
    elif stage == "inner_voice":
        print("  facts_used:", s.get("facts_used"))
        print("  voice_tokens:", s.get("voice_tokens"))
    elif stage == "dream":
        print("  sample_size:", s.get("sample_size"))
        print("  dream_tokens:", s.get("dream_tokens"))
