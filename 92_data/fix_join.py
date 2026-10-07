"""fix_join.py - fix literal \n\n -> real newlines in inner_voice.py."""
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

# 1. Заменяем литерал "\\n\\n" (4 символа в файле) на реальные переносы
#    В Python-строке файла это выглядит как: text = "\\n\\n".join(...)
#    В реальном тексте файла: backslash backslash n backslash backslash n
#    Ищем: '"\\\\n\\\\n"' (что в файле = "\\n\\n")
old_join = '"\\\\n\\\\n".join(lines_out)'
new_join = 'chr(10).join(lines_out) + chr(10)'.replace('chr(10).join', 'chr(10) + chr(10) + ""')  # placeholder

# Проще и надёжнее: заменяем строку целиком
old_line = 'text = "\\\\n\\\\n".join(lines_out)'
new_line = 'text = (chr(10) + chr(10)).join(lines_out)'

if old_line in text:
    text = text.replace(old_line, new_line)
    print("L85 fixed: literal \\n\\n -> real newlines")
else:
    # Пробуем другой вариант
    if '"\\\\n\\\\n"' in text:
        text = text.replace('"\\\\n\\\\n"', '(chr(10) + chr(10))')
        print("fixed via direct replace of \\\\n\\\\n")
    else:
        print("NOT FOUND: text = ...join(lines_out)")

# 2. Убираем лишнюю L78
old_l78 = '            content = content.replace("\\\\\\\\n", chr(10))\n'
if old_l78 in text:
    text = text.replace(old_l78, '')
    print("L78 removed")
else:
    # Пробуем более широкий поиск
    import re
    lines = text.split("\n")
    new_lines = []
    removed = 0
    for ln in lines:
        if 'content = content.replace("\\\\\\\\n", chr(10))' in ln:
            removed += 1
            continue
        new_lines.append(ln)
    if removed:
        text = "\n".join(new_lines)
        print("L78 removed via line filter:", removed)
    else:
        print("L78 not found (ok, may already be gone)")

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)

print("bytes:", os.path.getsize(path))