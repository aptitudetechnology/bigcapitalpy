import sys
import os

def check_init_files(root_dir, target_subdirs=None, max_depth=3):
    """
    Checks for missing __init__.py files under root_dir but only inside
    target_subdirs if given, and only up to max_depth levels deep.
    """
    print(f"=== Checking __init__.py under '{root_dir}' ===")
    missing_inits = []
    root_depth = root_dir.rstrip(os.sep).count(os.sep)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        depth = dirpath.count(os.sep) - root_depth
        if depth > max_depth:
            # Don't walk deeper than max_depth
            dirnames[:] = []
            continue
        
        # If target_subdirs is set, skip folders not in those subdirs
        if target_subdirs:
            rel_path = os.path.relpath(dirpath, root_dir)
            if not any(rel_path == d or rel_path.startswith(d + os.sep) for d in target_subdirs):
                continue
        
        # Ignore hidden dirs
        if any(part.startswith('.') for part in dirpath.split(os.sep)):
            continue
        
        # If folder contains .py files or subfolders, it should have __init__.py
        if any(f.endswith('.py') for f in filenames) or dirnames:
            if '__init__.py' not in filenames:
                missing_inits.append(dirpath)

    if missing_inits:
        print("Folders missing __init__.py:")
        for d in missing_inits:
            print(f"  - {d}")
    else:
        print("All relevant package folders have __init__.py")
    print()

def main():
    print("Python executable:", sys.executable)
    print("Current working directory:", os.getcwd())
    print()

    # Just print sys.path without too much detail
    print("sys.path summary:")
    for p in sys.path:
        print(f" - {p}")
    print()

    project_root = os.getcwd()  # adjust if needed

    # Focus on specific subdirs — customize as needed!
    subdirs_to_check = ['packages', 'packages/server', 'packages/server/src']
    
    check_init_files(project_root, target_subdirs=subdirs_to_check, max_depth=3)

if __name__ == "__main__":
    main()
