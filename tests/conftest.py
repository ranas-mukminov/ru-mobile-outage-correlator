import sys
from pathlib import Path

# Ensure the src/ directory is on the path for test runs without installation
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))
