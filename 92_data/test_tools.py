import sys
sys.path.insert(0, r"X:\08_tools")
import module as tools

print("=== TEST 1: now ===")
r = tools.now()
print(r)

print()
print("=== TEST 2: list_dir 10_projects ===")
r = tools.list_dir("10_projects")
if r["ok"]:
    print("count:", r["result"]["count"])
    for it in r["result"]["items"][:8]:
        print("  ", it)

print()
print("=== TEST 3: read_file book_iris/context.md ===")
r = tools.read_file("10_projects/books/book_iris/context.md")
if r["ok"]:
    print("bytes:", r["result"]["bytes"], "truncated:", r["result"]["truncated"])
    print(r["result"]["text"][:200])

print()
print("=== TEST 4: find_files meta ===")
r = tools.find_files("meta")
print(r)

print()
print("=== TEST 5: SECURITY - escape attempt ===")
for bad in [
    "00_dna/config.json",
    "01_core/active_model.txt",
    "../00_dna/config.json",
    "10_projects/../../00_dna/config.json",
]:
    r = tools.read_file(bad)
    print(bad, "->", "BLOCKED" if not r["ok"] else "LEAK!!! " + str(r)[:80])
