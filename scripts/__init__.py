"""Workspace entry points and legacy imports for the source-layout package."""

import sys
from pathlib import Path

# No installation required for the retained ``python -m scripts.<name>`` commands.
_source_root = str(Path(__file__).resolve().parents[1] / "src")
if _source_root not in sys.path:
    sys.path.insert(0, _source_root)
