import subprocess
import os
import sys

print("🔍 Running pycycle on this directory...")

target_dir = os.path.dirname(os.path.abspath(__file__))

try:
    result = subprocess.run(
        ["pycycle", "find", target_dir],
        capture_output=True,
        text=True,
        check=True
    )
    print(result.stdout)
    print("✅ pycycle finished without error.")
except subprocess.CalledProcessError as e:
    print(e.stdout)
    print(e.stderr)
    print("❌ pycycle exited with an error (code {})".format(e.returncode))
    sys.exit(1)
except FileNotFoundError:
    print("❌ pycycle is not installed or not in PATH.")
    print("💡 Try running: pip install pycycle")
    sys.exit(1)
