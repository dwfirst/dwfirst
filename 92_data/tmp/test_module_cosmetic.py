import sys
sys.path.insert(0, r"X:\08_tools")
import module
print("list_dir(path=10_projects):")
print("  ", module.call("list_dir", path="10_projects"))
print("read_file(path=...):")
print("  ", module.call("read_file", path="10_projects/books/book_iris/context.md"))