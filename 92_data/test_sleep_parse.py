import sys
sys.path.insert(0, r"X:\06_reflection")
sys.path.insert(0, r"X:\03_memory_working")
sys.path.insert(0, r"X:\01_core\modules")
import sleep

tests = [
    ("empty", ""),
    ("no json", "просто текст"),
    ("valid", '{"groups": [{"theme": "test", "ids": ["a", "b"]}]}'),
    ("with prefix", 'от результат: {"groups": [{"theme": "t2", "ids": ["x"]}]} конец'),
]

for name, text in tests:
    try:
        result = sleep._parse_groups(text)
        print(f"{name}: {result}")
    except Exception as e:
        print(f"{name}: ERROR {e}")