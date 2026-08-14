from __future__ import annotations

import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_ROOT = PROJECT_ROOT / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.chdir(PROJECT_ROOT)

from app import app as application  # noqa: E402


app = application


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000)
