"""night_mode.py - orchestrator for inner_voice + reverie.

Two modes:
  sleep   - only inner_voice, quiet. Short output.
  reverie - inner_voice + reverie. Fuller reflection.

Never touches session.log, window.jsonl, archive.jsonl.
Only writes to 03_memory_working via inner_voice / reverie.

API:
  run(llama, mode="sleep") -> dict
  mode: "sleep" | "reverie"
"""
import os
import sys
import time
import json

X = "X:" + os.sep
REFLECT_DIR = os.path.join(X, "06_reflection")
NIGHT_LOG = os.path.join(REFLECT_DIR, "night.log")

sys.path.insert(0, os.path.join(X, "01_core", "modules"))
sys.path.insert(0, os.path.join(X, "06_reflection"))


def _ensure_dir():
    if not os.path.isdir(REFLECT_DIR):
        os.makedirs(REFLECT_DIR, exist_ok=True)


def _run_inner_voice(llama, max_tokens=200):
    import inner_voice
    return inner_voice.run(llama, max_tokens=max_tokens)


def _run_reverie(llama, max_tokens=400):
    try:
        import reverie
    except ImportError:
        return {"ok": False, "reason": "no reverie module"}
    return reverie.run(llama, max_tokens=max_tokens)


def run(llama, mode="sleep"):
    """Run reflection stages. mode: 'sleep' or 'reverie'."""
    if mode not in ("sleep", "reverie"):
        return {"ok": False, "reason": "invalid mode: " + str(mode)}

    _ensure_dir()
    t0 = time.time()
    results = {}

    # --- Stage 1: inner_voice ---
    stage_start = time.time()
    try:
        if mode == "sleep":
            r = _run_inner_voice(llama, max_tokens=200)
        else:  # reverie
            r = _run_inner_voice(llama, max_tokens=300)
    except Exception as e:
        r = {"ok": False, "error": str(e)}
    r["stage"] = "inner_voice"
    r["stage_seconds"] = round(time.time() - stage_start, 1)
    results["inner_voice"] = r

    # --- Stage 2: reverie (only in reverie mode) ---
    if mode == "reverie":
        stage_start = time.time()
        try:
            r = _run_reverie(llama, max_tokens=400)
        except Exception as e:
            r = {"ok": False, "error": str(e)}
        r["stage"] = "reverie"
        r["stage_seconds"] = round(time.time() - stage_start, 1)
        results["reverie"] = r

    elapsed = round(time.time() - t0, 1)
    summary = {
        "ts": round(time.time(), 3),
        "date": time.strftime("%Y-%m-%d"),
        "mode": mode,
        "elapsed": elapsed,
        "results": results,
    }

    with open(NIGHT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(summary, ensure_ascii=False) + "\n")

    ok_count = sum(1 for r in results.values() if r.get("ok"))
    return {
        "ok": ok_count > 0,
        "mode": mode,
        "stages_run": len(results),
        "stages_ok": ok_count,
        "elapsed": elapsed,
        "results": results,
        "summary": {k: v.get("ok", False) for k, v in results.items()},
    }


if __name__ == "__main__":
    print("night_mode.py - module. Requires llama.")