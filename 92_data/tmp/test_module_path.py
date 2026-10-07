import sys
sys.path.insert(0, r"X:\08_tools")
import module

print("1. list_dir with rel_path:")
print("  ", module.call("list_dir", rel_path="10_projects"))

print("2. list_dir with path:")
print("  ", module.call("list_dir", path="10_projects"))

print("3. list_dir with unknown arg 'key':")
print("  ", module.call("list_dir", key="10_projects"))

print("4. read_file with path:")
print("  ", module.call("read_file", path="10_projects/books/book_iris/context.md"))

print("5. find_files with pattern:")
print("  ", module.call("find_files", pattern="context"))