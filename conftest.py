"""Repository-level pytest configuration.

Keeps the repository root importable so tests can import the ``scripts``
package (used by the release-workflow tests).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
