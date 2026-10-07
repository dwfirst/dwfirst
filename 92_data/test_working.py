import sys
sys.path.insert(0, r"X:\03_memory_working")
import working

r1 = working.add_fact("Обсуждали sliding window compaction", origin="diary", confidence="medium", tags=["memory"])
r2 = working.add_fact("Пользователь назвал себя Alex", origin="diary", confidence="medium", tags=["identity"])
r3 = working.add_fact("Я думала о том, почему он вернулся к теме памяти", origin="inner_voice", confidence="low")

print("--- stats ---")
print(working.stats())
print("--- active ---")
for r in working.get_active(days=7):
    print(r["id"], "|", r["origin"], "|", r["confidence"], "|", r["text"][:60])
print("--- inner_voice only ---")
for r in working.get_by_origin("inner_voice"):
    print(r["id"], "|", r["text"][:60])
