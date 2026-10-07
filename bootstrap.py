"""bootstrap.py - first-run setup for IRIS on a new PC.

Checks hardware, writes config if missing, installs missing packages,
downloads ONNX embedding model if not on X:.
Does NOT touch weights, archive, or chroma db.

Usage:
  python bootstrap.py           - normal run
  python bootstrap.py --check   - only check, no install
"""
import os
import sys
import json
import time
import subprocess
import argparse

X = "X:" + os.sep
PY = os.path.join(X, "00_python", "python.exe")
LOGS = os.path.join(X, "93_logs")
BOOT_LOG = os.path.join(LOGS, "bootstrap.log")
CFG = os.path.join(X, "00_dna", "config.json")
MODELS_DIR = os.path.join(X, "05_chroma", "models", "onnx_models", "all-MiniLM-L6-v2")


def log(msg):
    line = time.strftime("%H:%M:%S") + "  " + str(msg)
    print(line)
    try:
        os.makedirs(LOGS, exist_ok=True)
        with open(BOOT_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def detect_hardware():
    """Detect CPU cores and RAM."""
    try:
        import multiprocessing
        cores = multiprocessing.cpu_count()
    except Exception:
        cores = 2
    return {"cores": cores}


def suggest_threads(cores):
    """Suggest n_threads based on cores."""
    if cores <= 2:
        return 2
    if cores <= 4:
        return 3
    return 4


def ensure_config(hw):
    """Write config.json if missing. Never overwrite existing values."""
    if os.path.exists(CFG):
        log("config.json exists - keeping")
        return
    n_threads = suggest_threads(hw["cores"])
    cfg = {
        "model": {
            "backend": "llama-cpp-python",
            "n_ctx": 6000,
            "n_threads": n_threads,
            "temperature": 0.7,
            "top_p": 0.9,
            "gguf_dir": "X:" + os.sep + "01_core" + os.sep + "weights",
            "active_file": "X:" + os.sep + "01_core" + os.sep + "active_model.txt",
            "n_batch": 256,
            "verbose": False,
        },
        "memory": {
            "fast_max_messages": 40,
            "working_ttl_days": 7,
            "chroma_collection": "iris_memory",
        },
        "reflection": {
            "schedule": "03:00",
            "consolidate_after_days": 3,
        },
        "compaction": {
            "t_max": 3000,
            "t_retained": 1500,
            "summary_tokens": 300,
            "archive_originals": True,
        },
        "budget": {
            "role": 400,
            "retrieval": 1200,
            "window": 3000,
            "query": 500,
            "reserve": 600,
        },
    }
    with open(CFG, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    log("config.json written (n_threads=" + str(n_threads) + ")")


def check_package(name):
    try:
        __import__(name)
        return True
    except ImportError:
        return False


def check_dependencies(check_only=False):
    required = [
        ("llama_cpp", "llama-cpp-python"),
        ("chromadb", "chromadb"),
        ("onnxruntime", "onnxruntime"),
        ("streamlit", "streamlit"),
    ]
    missing = []
    for mod, pkg in required:
        if check_package(mod):
            log("  OK: " + pkg)
        else:
            log("  MISSING: " + pkg)
            missing.append(pkg)

    if missing and not check_only:
        log("Installing missing packages...")
        for pkg in missing:
            try:
                subprocess.check_call([PY, "-m", "pip", "install", "--no-cache-dir", pkg])
                log("  installed: " + pkg)
            except Exception as e:
                log("  FAILED: " + pkg + " - " + str(e))
    return missing


def ensure_onnx_model(check_only=False):
    """Check ONNX embedding model exists. Do not download here (chroma does it)."""
    if os.path.exists(MODELS_DIR):
        log("ONNX model found at " + MODELS_DIR)
        return True
    log("ONNX model NOT at " + MODELS_DIR)
    log("  (chroma will download on first use to " + MODELS_DIR + ")")
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    log("=== IRIS bootstrap ===")
    log("X: = " + X)

    hw = detect_hardware()
    log("hardware: cores=" + str(hw["cores"]))

    ensure_config(hw)

    missing = check_dependencies(check_only=args.check)
    ensure_onnx_model(check_only=args.check)

    if missing and args.check:
        log("Would install: " + ", ".join(missing))
    elif missing:
        log("Some packages failed - check above")
    else:
        log("All dependencies OK")

    log("=== done ===")


if __name__ == "__main__":
    main()
