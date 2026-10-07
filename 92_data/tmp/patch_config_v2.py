# patch_config_v2.py - поднять core до 600, retrieval до 1600
import io, json, os

X = "X:" + os.sep
p = os.path.join(X, "00_dna", "config.json")

with io.open(p, "r", encoding="utf-8-sig") as f:
    cfg = json.load(f)

cfg["budget"]["core"] = 600
cfg["budget"]["retrieval"] = 1600

with io.open(p, "w", encoding="utf-8") as f:
    json.dump(cfg, f, ensure_ascii=False, indent=2)

print("patched_config_v2 OK")
print("budget:", cfg["budget"])
print("sum:", sum(cfg["budget"].values()))