# check_cycles.py

import os
import sys

print("🔍 Running pycycle on this directory...")

try:
    from pycycle.cli import main
except ImportError:
    print("❌ pycycle is not installed. Run: pip install pycycle")
    sys.exit(1)

# Set target directory to the current directory
target_dir = os.path.dirname(__file__) or '.'

# Run pycycle on this directory
sys.argv = ['pycycle', target_dir]
main()
