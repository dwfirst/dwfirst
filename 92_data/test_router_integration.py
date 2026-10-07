import sys
sys.path.insert(0, r"X:\01_core\modules")
import brain

brain.reset()
brain.storage.reset_session()

# Force role = None (auto mode)
import json
sp = r"X:\07_router\state.json"
with open(sp, "r", encoding="utf-8-sig") as f:
    st = json.load(f)
st["role"]["active"] = ""
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=2)
print("role cleared -> auto mode")

# Test 1: poet
r = brain.chat_one("\u041d\u0430\u043f\u0438\u0448\u0438 \u0441\u0442\u0438\u0445 \u043f\u0440\u043e \u043f\u0430\u043c\u044f\u0442\u044c", max_tokens=80)
print("--- TEST 1: poet ---")
print("routing:", r.get("routing"))
print("answer[:100]:", r["text"][:100])
