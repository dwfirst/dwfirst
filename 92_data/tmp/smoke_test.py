import sys
sys.path.insert(0, r"X:\01_core\modules")
import brain
r = brain.chat_one("Привет. Одно слово.", max_tokens=20)
print("TEXT:", r["text"][:200])
print("BUDGET:", r["budget"])
print("ROUTING:", r.get("routing"))