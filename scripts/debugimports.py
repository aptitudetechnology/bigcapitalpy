import sys
import os

def check_sys_path():
    print("=== sys.path directories ===")
    for p in sys.path:
        print(p)
    print()

def check_init_files(root_dir):
    print(f"=== Checking for __init__.py files under '{root_dir}' ===")
    missing_inits = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignore hidden dirs
        if any(part.startswith('.') for part in dirpath.split(os.sep)):
            continue
        # Check if this folder looks like a package folder (has .py files or subfolders)
        if any(f.endswith('.py') for f in filenames) or dirnames:
            if '__init__.py' not in filenames:
                missing_inits.append(dirpath)
    if missing_inits:
        print("Folders missing __init__.py:")
        for d in missing_inits:
            print(f"  - {d}")
    else:
        print("All package folders have __init__.py")
    print()

def main():
    print("Python executable:", sys.executable)
    print("Current working directory:", os.getcwd())
    print()
    check_sys_path()

    # Check __init__.py under the current directory or a specified folder
    project_root = os.getcwd()  # adjust if needed
    check_init_files(project_root)

if __name__ == "__main__":
    main()
