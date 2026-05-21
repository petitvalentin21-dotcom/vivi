from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Provide a test encryption key so create_app() doesn't exit during test collection.
# Must be set before any test module that imports app.api.server.
os.environ.setdefault("VIVI_LOG_ENCRYPTION_KEY", "pytest-test-encryption-key-do-not-use")
