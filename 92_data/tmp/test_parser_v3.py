import sys
sys.path.insert(0, r"X:\08_tools")
import parser

tests = [
    "Hello. [[TOOL: now]] done.",
    "Hello. [TOOL: now] done.",
    "[[TOOL: list_dir, path=10_projects]]",
    "[[TOOL: read_file, path=10_projects/books/book_iris/context.md]]",
    "[[TOOL: find_files, pattern=meta]]",
    "[[TOOL: list_dir, key=10_projects]]",   # мусорный ключ
    "[TOOL_CALL]\nnow()",
    "[TOOL_CALL]\nlist_dir(10_projects/books/book_iris)",
]
for t in tests:
    print("IN:", repr(t))
    print("  ", parser.parse(t))