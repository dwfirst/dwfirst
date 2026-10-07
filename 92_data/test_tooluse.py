import sys
sys.path.insert(0, r"X:\01_core\modules")
import brain

brain.reset()
brain.storage.reset_session()

# Test 1: natural question -> model should call `now`
r = brain.chat_one(
    "Сколько сейчас времени? Используй инструмент.",
    max_tokens=200,
)
print("=== TEST 1: now (natural) ===")
print("ANSWER:", r["text"])
print("tool_use:", r["tool_use"])
print()

# Test 2: list project files
r2 = brain.chat_one(
    "Покажи, что лежит в папке 10_projects/books/book_iris.",
    max_tokens=300,
)
print("=== TEST 2: list_dir (natural) ===")
print("ANSWER:", r2["text"])
print("tool_use:", r2["tool_use"])
print()

# Test 3: read a file
r3 = brain.chat_one(
    "Прочитай файл 10_projects/books/book_iris/context.md и перескажи.",
    max_tokens=300,
)
print("=== TEST 3: read_file (natural) ===")
print("ANSWER:", r3["text"])
print("tool_use:", r3["tool_use"])