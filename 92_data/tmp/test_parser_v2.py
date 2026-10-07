import sys
sys.path.insert(0, r"X:\08_tools")
import parser

tests = [
    "Hello. [[TOOL: now]] done.",
    "Hello. [TOOL: now] done.",
    "[TOOL_CALL]\nnow()",
    "[TOOL_CALL]\nlist_dir(10_projects/books/book_iris)",
    "[TOOL_CALL]\nread_file(path=10_projects/books/book_iris/context.md)",
]
for t in tests:
    print("IN:", repr(t))
    print("  ", parser.parse(t))