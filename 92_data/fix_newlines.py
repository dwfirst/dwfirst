"""fix_newlines.py - right fix for inner_voice newlines."""
import os
import shutil
import datetime

path = r"X:\06_reflection\inner_voice.py"
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
backup = path + ".bak_" + stamp
shutil.copy2(path, backup)
print("backup:", backup)

with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Ищем строку content = (rec.get("content") or "").strip()
old = '            content = (rec.get("content") or "").strip()'
new = old + '\n            content = content.replace(chr(92) + "n", chr(10))'

if old in text:
    # Проверяем, не добавлено ли уже
    if 'content.replace(chr(92)' not in text and 'content.replace("\\\\n"' not in text:
        text = text.replace(old, new)
        print("fix added (via chr(92))")
    else:
        # Уже есть фикс — заменяем на правильный
        import re
        text = re.sub(r'            content = content\.replace\([^\n]+\)\n', '', text)
        text = text.replace(old, new)
        print("fix replaced with correct one")
else:
    print("ERROR: old line not found")

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)

print("bytes:", os.path.getsize(path))