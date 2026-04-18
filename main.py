from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
PYTHON_DIR = ROOT_DIR / "python"

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from app import app  # noqa: E402


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
