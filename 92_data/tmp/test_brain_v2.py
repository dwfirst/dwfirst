# test_brain_v2.py
import sys, os
sys.path.insert(0, r"X:\01_core\modules")
import brain

r = brain.chat_one("Одно слово: кто ты?", max_tokens=30)
print("TEXT:", r["text"])
print("TOKENS:", r.get("completion_tokens"))
print("SECONDS:", r.get("seconds"))
print("TPS:", r.get("tps"))
print("BUDGET:", r["budget"])