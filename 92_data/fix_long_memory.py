import os
import shutil
import datetime

path = r"X:\04_memory_long\long_memory.py"
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
backup = path + ".bak_" + stamp
shutil.copy2(path, backup)
print("backup:", backup)

with open(path, "r", encoding="utf-8") as f:
    text = f.read()

if "def rebuild_index" in text:
    print("already exists — skip")
    exit(0)

# Функция rebuild_index
new_func = '''def rebuild_index():
    """Recount index.json from archive.jsonl. Use after manual edits."""
    _ensure_dir()
    total = 0
    first_ts = None
    last_ts = None
    days = []
    if os.path.exists(ARCHIVE):
        with open(ARCHIVE, "r", encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                total += 1
                ts = rec.get("ts")
                if ts:
                    if first_ts is None or ts < first_ts:
                        first_ts = ts
                    if last_ts is None or ts > last_ts:
                        last_ts = ts
                d = rec.get("date")
                if d and d not in days:
                    days.append(d)
    idx = {
        "total": total,
        "first_ts": first_ts,
        "last_ts": last_ts,
        "days": sorted(days),
    }
    _save_index(idx)
    return idx


'''

# Вставляем перед "def stats():"
old = "def stats():"
if old not in text:
    print("ERROR: def stats() not found")
    exit(1)

text = text.replace(old, new_func + old, 1)

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)

print("OK — rebuild_index added")
print("bytes:", os.path.getsize(path))