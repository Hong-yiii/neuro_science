#!/usr/bin/env python3
# pyright: reportMissingImports=false
"""Compatibility CLI/import alias for :mod:`neuro.studies.endpoint_time_readout`."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import scripts  # noqa: F401 — bootstrap src for direct/bare legacy callers

from neuro.studies import endpoint_time_readout as _implementation
from neuro.studies.endpoint_time_readout import *  # noqa: F401,F403 — static legacy exports

if __name__ == "__main__":
    _implementation.main()
else:
    # Module identity preserves private exports, monkeypatches and old pickle lookups.
    sys.modules[__name__] = _implementation
