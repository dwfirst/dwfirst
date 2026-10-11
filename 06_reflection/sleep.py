"""sleep.py - L1: memory consolidation.

Reads facts.jsonl (last N days), groups by theme, compresses each group.
Writes consolidated facts with origin="consolidated".
Archives source facts (not deletes).

No dialogue. No questions. Only processing.

API:
  run(llama, days=7, max_groups=5) -> dict
"""
import os
import sys
import time
import json
import re

X = "X:" + os.sep
REFLECT_DIR = os.path.join(X, "06_reflection")
SLEEP_LOG = os.path.join(REFLECT_DIR, "sleep.log")

sys.path.insert(0, os.path.join(X, "01_core", "modules"))
sys.path.insert(0, os.path.join(X, "03_memory_working"))

import working
from infer import generate


GROUP_PROMPT = """Ты — система консолидации памяти Айрис. Вот факты за последние дни.

{facts}

Сгруппируй их по смысловым темам. Каждая тема — от 2 до 8 фактов.
Названия тем — короткие (3-6 слов).

Формат ответа — строго JSON:
{{"groups": [{{"theme": "...", "ids": ["id1", "id2"]}}, ...]}}

Только JSON. Без пояснений."""


COMPRESS_PROMPT = """Ты — система консолидации памяти Айрис.

Тема: {theme}

Факты:
{facts}

Сожми эти факты в 1-2 плотных предложения. Сохрани суть, имена, даты, связи.
Пиши на русском. Без воды.

Результат:"""


def _today():
    return time.strftime("%Y-%m-%d")


def _ensure_dir():
    if not os.path.isdir(REFLECT_DIR):
        os.makedirs(REFLECT_DIR, exist_ok=True)


def _format_facts(facts):
    lines = []
    for f in facts:
        fid = f.get("id", "?")
        origin = f.get("origin", "?")
        text = (f.get("text") or "")[:300].replace("\n", " ")
        lines.append(f"[{fid}] ({origin}) {text}")
    return "\n".join(lines)


def _parse_groups(text):
    """Extract JSON from LLM output."""
    # Ищем JSON в тексте
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if not m:
        return []
    try:
        data = json.loads(m.group(0))
        groups = data.get("groups", [])
        if isinstance(groups, list):
            return groups
    except Exception:
        pass
    return []


def run(llama, days=7, max_groups=5):
    """Consolidate facts for last N days."""
    _ensure_dir()
    t0 = time.time()

    facts = working.get_active(days=days)
    if len(facts) < 5:
        return {"ok": False, "reason": "too few facts: " + str(len(facts))}

    # 1. Группировка
    facts_text = _format_facts(facts)[:4000]
    prompt = GROUP_PROMPT.format(facts=facts_text)

    r1 = generate(llama, [{"role": "user", "content": prompt}],
                  max_tokens=600, temperature=0.3)
    groups_raw = r1["text"].strip()

    groups = _parse_groups(groups_raw)
    if not groups:
        return {"ok": False, "reason": "no groups parsed", "raw": groups_raw[:300]}

    groups = groups[:max_groups]

    # 2. Сжатие каждой группы
    consolidated = []
    archived_ids = []

    for g in groups:
        theme = g.get("theme", "?")
        ids = g.get("ids", [])
        if not ids:
            continue

        group_facts = working.get_by_ids(ids)
        if not group_facts:
            continue

        group_text = _format_facts(group_facts)[:3000]
        prompt2 = COMPRESS_PROMPT.format(theme=theme, facts=group_text)

        r2 = generate(llama, [{"role": "user", "content": prompt2}],
                      max_tokens=200, temperature=0.4)
        compressed = r2["text"].strip()

        if not compressed:
            continue

        fact = working.add_fact(
            compressed,
            origin="consolidated",
            confidence="medium",
            tags=["consolidated", theme, _today()],
            date=_today(),
        )

        consolidated.append({
            "theme": theme,
            "source_count": len(group_facts),
            "fact_id": fact["id"] if fact else None,
            "preview": compressed[:200],
        })
        archived_ids.extend(ids)

    # 3. Архивировать исходные
    archived_count = working.archive_facts(archived_ids)

    elapsed = round(time.time() - t0, 1)
    log_rec = {
        "ts": round(time.time(), 3),
        "date": _today(),
        "days": days,
        "facts_input": len(facts),
        "groups": len(groups),
        "consolidated": len(consolidated),
        "archived": archived_count,
        "elapsed": elapsed,
        "details": consolidated,
    }
    with open(SLEEP_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_rec, ensure_ascii=False) + "\n")

    return {
        "ok": len(consolidated) > 0,
        "date": _today(),
        "facts_input": len(facts),
        "groups": len(groups),
        "consolidated": len(consolidated),
        "archived": archived_count,
        "elapsed": elapsed,
        "preview": consolidated[:3],
    }


if __name__ == "__main__":
    print("sleep.py - module. Requires llama.")