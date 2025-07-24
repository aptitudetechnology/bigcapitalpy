import os
from pycycle import analyze

print("🔍 Running pycycle on this directory...\n")

target_dir = os.path.dirname(__file__) or "."

cycles = analyze(target_dir)

if cycles:
    print("🔁 Circular imports detected:\n")
    for cycle in cycles:
        print(" → ".join(cycle))
    print("\n❌ Please resolve these cycles.")
else:
    print("✅ No circular imports detected.")
