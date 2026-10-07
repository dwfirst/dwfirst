import os, shutil
X = "X:" + os.sep
removed_dirs = 0
removed_files = 0
for r, dirs, files in os.walk(X):
    if "92_data" + os.sep + "tmp" in r:
        continue
    if "__pycache__" in dirs:
        p = os.path.join(r, "__pycache__")
        try:
            shutil.rmtree(p)
            removed_dirs += 1
        except Exception as e:
            print("ERR dir:", p, e)
    for x in files:
        if x.endswith(".pyc"):
            try:
                os.remove(os.path.join(r, x))
                removed_files += 1
            except Exception as e:
                print("ERR file:", x, e)
print("removed dirs:", removed_dirs)
print("removed pyc files:", removed_files)