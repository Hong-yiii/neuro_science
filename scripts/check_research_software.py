"""Run synthetic/software checks without requiring private lab inputs or a GPU."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from cases(item)
        else:
            yield item


if __name__ == "__main__":
    # These two historical checks require ignored lab inputs, not clone-only software.
    local_only = {
        "test_actual_input_gate",
        "test_saved_manifest_has_seven_session_components_per_pseudorow",
    }
    discovered = unittest.defaultTestLoader.discover(
        str(ROOT / "scripts"), pattern="test_*.py", top_level_dir=str(ROOT)
    )
    suite = unittest.TestSuite(
        case
        for case in cases(discovered)
        if case.id().rsplit(".", 1)[-1] not in local_only
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(not result.wasSuccessful())
