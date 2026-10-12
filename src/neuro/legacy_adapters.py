"""Audited boundary to retained place195/CEBRA helpers outside this package.

These are the original functions, not copies. Importing them opens no lab files
and performs no fits; calling the raw readers explicitly opens supplied paths.
The source checkout remains required until these older families are migrated.
See README.md for the dependency inventory and historical-source limits.
"""

import sys
from pathlib import Path

# Allow PYTHONPATH=/checkout/src imports from another working directory too.
_checkout = str(Path(__file__).resolve().parents[2])
if _checkout not in sys.path:
    sys.path.insert(0, _checkout)

from scripts.import_place195_sessions import (  # noqa: E402,F401
    _codes_at,
    _times_at,
    read_ripple_trials,
    read_spiketrain,
    spikes_in_window,
)
from scripts.import_place195_sessions import (  # noqa: E402,F401
    _csv_value as imported_csv_value,
)
from scripts.place195_v7_v8_neural_experiments import (  # noqa: E402,F401
    bin_events,
    session_from_cell,
)
from scripts.place195_v8b_v9_cebra import make_solver  # noqa: E402,F401


def geometry_helpers():
    """Load atlas diagnostics only for the cue-time study, not other workflows."""
    from scripts.cebra_latent_atlas import fidelity, spectrum

    return fidelity, spectrum
