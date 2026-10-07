"""Патч brain.py: добавляет управление моделями.
Запускается один раз. Делает backup .bak_ перед правкой.
"""
import os
import sys
import shutil
import datetime

BRAIN = r"X:\01_core\modules\brain.py"

# --- 1. Backup ---
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BRAIN + f".bak_{stamp}"
shutil.copy2(BRAIN, backup)
print(f"[patch] backup: {backup}")

# --- 2. Читаем ---
with open(BRAIN, "r", encoding="utf-8-sig") as f:
    text = f.read()

# --- 3. Правка reset() ---
old_reset = '''def reset():
    global _LLAMA, _META
    _LLAMA = None
    _META = None'''

new_reset = '''def reset():
    """Выгрузить модель из RAM немедленно."""
    global _LLAMA, _META
    if _LLAMA is not None:
        try:
            _LLAMA.close()
        except Exception:
            pass
    _LLAMA = None
    _META = None
    import gc
    gc.collect()'''

if old_reset not in text:
    print("[patch] ОШИБКА: не нашёл старый reset(). Проверь вручную.")
    sys.exit(1)

text = text.replace(old_reset, new_reset)
print("[patch] reset() обновлён")

# --- 4. Добавляем функции в конец ---
addition = '''

# ---------- УПРАВЛЕНИЕ МОДЕЛЯМИ ----------

def list_models(weights_dir=None):
    """Список .gguf в папке моделей."""
    if weights_dir is None:
        weights_dir = os.path.join(X, "01_core", "weights")
    if not os.path.isdir(weights_dir):
        return []
    return sorted([f for f in os.listdir(weights_dir) if f.lower().endswith(".gguf")])


def current_model():
    """Имя файла текущей модели или None."""
    global _META
    if _META is None:
        return None
    return _META.get("model")


def load_model_by_name(model_name, weights_dir=None):
    """Выгрузить текущую модель, загрузить новую. Возвращает (ok, message)."""
    if weights_dir is None:
        weights_dir = os.path.join(X, "01_core", "weights")
    path = os.path.join(weights_dir, model_name)
    if not os.path.exists(path):
        return False, "Файл не найден: " + path

    # 1. Выгрузить
    reset()

    # 2. Обновить active_model.txt
    try:
        active_file = os.path.join(X, "01_core", "active_model.txt")
        with open(active_file, "w", encoding="utf-8") as f:
            f.write(model_name)
    except Exception as e:
        return False, "Не могу записать active_model.txt: " + str(e)

    # 3. Загрузить
    try:
        llama, meta = get_llama(verbose=False)
        if llama is None:
            return False, "load_model вернул None"
        return True, "Загружено: " + model_name
    except Exception as e:
        return False, "Ошибка загрузки: " + str(e)[:160]
'''

# Проверяем, что ещё не добавлено
if "def load_model_by_name" in text:
    print("[patch] функции уже добавлены — пропускаю")
else:
    text = text.rstrip() + "\n" + addition
    print("[patch] добавлены list_models / current_model / load_model_by_name")

# --- 5. Записываем без BOM ---
with open(BRAIN, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)

print("[patch] ГОТОВО")
print(f"[patch] размер: {os.path.getsize(BRAIN)} байт")