#!/usr/bin/env python3

"""
Run pycycle to detect circular imports in this directory.
"""

import sys
import subprocess

def main():
    try:
        import pycycle  # noqa: F401
    except ImportError:
        print("❌ pycycle is not installed in this environment. Run: pip install pycycle")
        sys.exit(1)

    print("🔍 Running pycycle on this directory...")
    try:
        subprocess.run([
            sys.executable, "-m", "pycycle.cli", "check", "."
        ], check=True)
    except subprocess.CalledProcessError as e:
        print("⚠️ Circular import(s) found.")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
