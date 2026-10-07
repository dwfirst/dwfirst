import sys
sys.path.insert(0, r"X:\01_core\modules")
import brain

print("=== BUDGET ===")
print(brain._load_budget())
print()
print("=== SYSTEM MESSAGE (split) ===")
try:
    p = brain.build_system_message(split=True)
    print("core:", len(p.get("core", "")), "chars")
    print("role:", len(p.get("role", "")), "chars")
    print("project:", len(p.get("project", "")), "chars")
    print()
    print("--- core preview ---")
    print(p.get("core", "")[:200])
except Exception as e:
    print("ERROR:", e)
    import traceback
    traceback.print_exc()
