# check_cycles.py

import subprocess
import os

print("🔍 Running pycycle on this directory...")

target_dir = os.path.dirname(__file__) or "."

try:
    result = subprocess.run(
        ["pycycle", target_dir],
        check=True,
        capture_output=False,  # set to True if you want to suppress output and capture it
    )
except FileNotFoundError:
    print("❌ pycycle is not installed or not in PATH. Try running: pip install pycycle")
except subprocess.CalledProcessError as e:
    print(f"❌ pycycle exited with an error (code {e.returncode})")
