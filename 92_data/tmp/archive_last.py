import json
X = "X:" + chr(92)
p = X + "04_memory_long" + chr(92) + "archive.jsonl"
lines = []
with open(p, "r", encoding="utf-8-sig") as f:
    for line in f:
        if line.strip():
            lines.append(line)
print("total lines:", len(lines))
for line in lines[-3:]:
    r = json.loads(line)
    print("---")
    print("keys:", list(r.keys()))
    for k, v in r.items():
        if isinstance(v, str):
            print(" ", k, "=", repr(v[:100]))
        else:
            print(" ", k, "=", v)