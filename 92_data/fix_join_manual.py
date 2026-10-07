import os
import shutil
import datetime

path = r"X:\06_reflection\inner_voice.py"
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy2(path, path + ".bak_" + stamp)

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for ln in lines:
    # L85: заменяем join
    if 'join(lines_out)' in ln and 'text =' in ln:
        # Ставим правильный вариант
        indent = ln[:len(ln) - len(ln.lstrip())]
        new_lines.append(indent + 'text = (chr(10) + chr(10)).join(lines_out)\n')
        print("L join fixed")
    # L78: убираем лишний replace
    elif 'content.replace("\\\\\\\\n"' in ln or 'content.replace("\\\\n"' in ln and 'chr(92)' not in ln:
        print("L78 removed:", ln.strip()[:60])
        continue
    else:
        new_lines.append(ln)

with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(new_lines)

print("bytes:", os.path.getsize(path))