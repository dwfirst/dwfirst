"""loader.py — загрузка GGUF-модели через llama-cpp-python.
Единственная задача: вернуть объект Llama. Без логики диалога.
"""
import os
import json
import time

X = "X:" + os.sep

def _read_config():
    cfg_path = os.path.join(X, "00_dna", "config.json")
    with open(cfg_path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def _read_active_model():
    active_path = os.path.join(X, "01_core", "active_model.txt")
    with open(active_path, "r", encoding="utf-8-sig") as f:
        return f.read().strip()

def load_model(verbose=True):
    """Загружает активную GGUF-модель. Возвращает (llama, meta)."""
    from llama_cpp import Llama

    cfg = _read_config()
    m = cfg["model"]

    model_name = _read_active_model()
    model_path = os.path.join(m["gguf_dir"], model_name)
    if not os.path.exists(model_path):
        raise FileNotFoundError("Модель не найдена: " + model_path)

    if verbose:
        print("[loader] модель:", model_name)
        print("[loader] путь:", model_path)
        print("[loader] n_ctx =", m["n_ctx"], "| n_threads =", m["n_threads"])

    t0 = time.time()
    llama = Llama(
        model_path=model_path,
        n_ctx=m["n_ctx"],
        n_threads=m["n_threads"],
        n_batch=m.get("n_batch", 256),
        verbose=m.get("verbose", False),
    )
    load_time = time.time() - t0

    meta = {
        "model": model_name,
        "n_ctx": m["n_ctx"],
        "n_threads": m["n_threads"],
        "load_seconds": round(load_time, 2),
    }

    if verbose:
        print("[loader] загружено за", meta["load_seconds"], "сек")

    return llama, meta


if __name__ == "__main__":
    llama, meta = load_model(verbose=True)
    print("[loader] OK:", meta)
