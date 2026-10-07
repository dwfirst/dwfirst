import json
X = "X:" + chr(92)
p = X + "04_memory_long" + chr(92) + "archive.jsonl"
with open(p, "r", encoding="utf-8-sig") as f:
    for i, line in enumerate(f):
        if not line.strip():
            continue
        r = json.loads(line)
        print("KEYS:", list(r.keys()))
        print(json.dumps(r, ensure_ascii=False, indent=2)[:800])
        break