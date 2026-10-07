"""router.py - keyword-based auto-selection of role / project / retrieval filter.

No model. Fast (pure string matching).

API:
  route(query, current_role=None, current_project=None) -> dict
    returns {
      "role": str | None,
      "project": str | None,
      "retrieval_filter": str | None,
      "confidence": float,
      "reason": str
    }
"""
import os
import json

X = "X:" + os.sep
RULES_FILE = os.path.join(X, "07_router", "role_rules.json")

_RULES = None


def _load_rules():
    global _RULES
    if _RULES is None:
        with open(RULES_FILE, "r", encoding="utf-8-sig") as f:
            _RULES = json.load(f)
    return _RULES


def _norm(text):
    return (text or "").lower().strip()


def _match_role(query):
    rules = _load_rules()
    roles = rules.get("roles", {})
    q = _norm(query)
    best_role = None
    best_score = 0
    best_kw = None
    for role, info in roles.items():
        kws = info.get("keywords", [])
        priority = info.get("priority", 1)
        hits = 0
        hit_kw = None
        for kw in kws:
            if kw in q:
                hits += 1
                if hit_kw is None:
                    hit_kw = kw
        if hits == 0:
            continue
        score = hits * priority
        if score > best_score:
            best_score = score
            best_role = role
            best_kw = hit_kw
    if best_role is None:
        return None, 0.0, None
    confidence = min(1.0, best_score / 20.0)
    return best_role, confidence, best_kw


def _match_project(query):
    rules = _load_rules()
    projects = rules.get("projects", {})
    q = _norm(query)
    for proj_id, kws in projects.items():
        for kw in kws:
            if kw in q:
                return proj_id, kw
    return None, None


def _match_retrieval(query):
    rules = _load_rules()
    rr = rules.get("retrieval_rules", {})
    q = _norm(query)
    for origin, patterns in rr.items():
        for p in patterns:
            if p in q:
                return origin, p
    return None, None


def route(query, current_role=None, current_project=None):
    """Determine role/project/retrieval filter from query text."""
    q = _norm(query)
    if not q:
        return {
            "role": current_role,
            "project": current_project,
            "retrieval_filter": None,
            "confidence": 0.0,
            "reason": "empty query",
        }

    role, rconf, rkw = _match_role(q)
    proj, pkw = _match_project(q)
    retr, rtrkw = _match_retrieval(q)

    reasons = []
    if role:
        reasons.append("role=" + role + " (" + str(rkw) + ")")
    if proj:
        reasons.append("project=" + proj + " (" + str(pkw) + ")")
    if retr:
        reasons.append("retrieval=" + retr + " (" + str(rtrkw) + ")")

    return {
        "role": role or current_role,
        "project": proj or current_project,
        "retrieval_filter": retr,
        "confidence": rconf,
        "reason": "; ".join(reasons) if reasons else "no matches, keep current",
    }


def reload_rules():
    global _RULES
    _RULES = None
    return _load_rules()


if __name__ == "__main__":
    tests = [
        "Напиши стих про память",
        "Что я писал про compaction?",
        "Помоги с кодом на Python",
        "О чём ты думала ночью?",
        "Расскажи про архитектуру проекта",
    ]
    for t in tests:
        r = route(t)
        print(t)
        print("  ", r)
