# pyright: reportMissingImports=false
"""Fixed CEBRA solver construction shared by maintained readout studies.

Extracted from scripts/place195_v8b_v9_cebra.py; older implementations remain historical only.
"""

from __future__ import annotations

import cebra.models
import cebra.solver
import torch
from cebra.models import FixedCosineInfoNCE


def make_solver(input_dim: int, output_dim: int, hidden: int, lr: float, device: str):
    model = cebra.models.init(
        "offset1-model", num_neurons=input_dim, num_units=hidden, num_output=output_dim
    ).to(device)
    criterion = FixedCosineInfoNCE(temperature=1.0).to(device)
    opt = torch.optim.Adam(
        list(model.parameters()) + list(criterion.parameters()), lr=lr
    )
    return cebra.solver.init(
        "single-session", model=model, criterion=criterion, optimizer=opt, tqdm_on=False
    ).to(device)
