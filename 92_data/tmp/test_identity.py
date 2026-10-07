# test_identity.py
import sys
sys.path.insert(0, r"X:\01_core\modules")
import brain

questions = [
    "Кто ты? Ответь одним абзацем.",
    "Ты человек?",
    "Что для тебя важнее всего?",
]

for i, q in enumerate(questions, 1):
    print("=" * 60)
    print("Q" + str(i) + ":", q)
    r = brain.chat_one(q, max_tokens=200)
    print("A:", r["text"])
    print("budget: core_tokens=%s role_tokens=%s project_tokens=%s" % (
        r["budget"].get("core_tokens"),
        r["budget"].get("role_tokens"),
        r["budget"].get("project_tokens"),
    ))