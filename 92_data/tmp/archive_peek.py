import json
X = "X:" + chr(92)
p = X + "04_memory_long" + chr(92) + "archive.jsonl"
n = 0
with open(p, "r", encoding="utf-8-sig") as f:
    for line in f:
        if not line.strip():
            continue
        n += 1
        if n <= 5:
            r = json.loads(line)
            print("---", n, "---")
            print("role:", r.get("role"))
            print("ts:", r.get("ts"))
            print("text[:120]:", r.get("text", "")[:120])
            print()
print("total:", n)