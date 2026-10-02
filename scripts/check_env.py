"""Quick sanity check: are the Step 1 packages installed and importable?"""
import sys

print("Python:", sys.version.split()[0])
print("Interpreter:", sys.executable)

for name in ["pandas", "numpy", "sklearn", "joblib", "dotenv"]:
    try:
        module = __import__(name)
        version = getattr(module, "__version__", "installed")
        print(f"OK   {name:<8} {version}")
    except ImportError:
        print(f"FAIL {name:<8} not installed")

if ".venv" not in sys.executable:
    print("\nWARNING: you are not inside the .venv virtual environment.")
