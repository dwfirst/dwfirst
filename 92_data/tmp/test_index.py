import sys
sys.path.insert(0, r"X:\01_core\modules")
import brain

# Очищаем сессию (чтобы не путаться с архивом)
brain.storage.reset_session()

# Тест 1: простой диалог
r1 = brain.chat_one("Что такое память? Ответь одним предложением.", max_tokens=80)
print("Q1:", "Что такое память?")
print("A1:", r1["text"][:150])
print()

# Тест 2: второй диалог
r2 = brain.chat_one("А что такое архив?", max_tokens=80)
print("Q2:", "А что такое архив?")
print("A2:", r2["text"][:150])
print()

# Проверка Chroma
sys.path.insert(0, r"X:\05_chroma")
import chroma_store
print("Chroma count:", chroma_store.count())
print()
print("Search 'память':")
for item in chroma_store.search("память", top_k=5):
    meta = item.get("metadata", {})
    print("  id:", item.get("id"))
    print("    origin:", meta.get("origin"), "| source:", meta.get("source"))
    print("    text[:80]:", item.get("text", "")[:80])