# check_cycles.py

import subprocess
import os

print("🔍 Running pycycle on this directory...")

target_dir = os.path.dirname(__file__) or "."

try:
    result = subprocess.run(
        ["pycycle", "find", target_dir],
        check=True,
    )
except FileNotFoundError:
    print("❌ pycycle is not installed or not in PATH. Try running: pip install pycycle")
except subprocess.CalledProcessError as e:
    print(f"❌ pycycle exited with an error (code {e.returncode})")
