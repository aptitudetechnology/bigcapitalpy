#!/usr/bin/env python3
"""
Check for circular imports in the reports module using pycycle.
"""

import sys
from pathlib import Path

# Ensure pycycle is installed
try:
    from pycycle import find_cycles
except ImportError:
    print("❌ pycycle is not installed. Run: pip install pycycle")
    sys.exit(1)

# Set the base directory
BASE_DIR = Path(__file__).resolve().parent

# Run cycle detection
print(f"🔍 Checking for circular imports under: {BASE_DIR}")

cycles = find_cycles(str(BASE_DIR))

if not cycles:
    print("✅ No circular import cycles detected.")
else:
    print("🚨 Circular import cycles found:")
    for cycle in cycles:
        print(" -> ".join(cycle))
