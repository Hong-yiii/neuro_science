#!/usr/bin/env python3
"""Compatibility import for :mod:`neuro.place195_split_access` (no CLI work)."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import scripts  # noqa: F401 — bootstrap src for legacy bare imports/execution

from neuro import place195_split_access
from neuro.place195_split_access import DEVELOPMENT_SPLITS as DEVELOPMENT_SPLITS
from neuro.place195_split_access import TABLE_FILENAMES as TABLE_FILENAMES
from neuro.place195_split_access import SplitAccessError as SplitAccessError
from neuro.place195_split_access import SplitFilteredAccess as SplitFilteredAccess
from neuro.place195_split_access import SplitFilteredAudit as SplitFilteredAudit

# Preserve one module/class identity, including private helper and pickle lookups.
sys.modules[__name__] = place195_split_access
