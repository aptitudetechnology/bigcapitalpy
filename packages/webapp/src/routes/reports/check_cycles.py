#!/usr/bin/env python3
import sys
import subprocess

def main():
    print("🔍 Running pycycle on this directory...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pycycle.cli", "check", "."],
            check=True
        )
    except subprocess.CalledProcessError:
        print("⚠️ Circular import(s) found.")
        sys.exit(1)

if __name__ == "__main__":
    main()
