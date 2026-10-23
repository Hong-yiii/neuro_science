"""Shape-matched invented full-grid benchmark; never opens biological neural inputs.

Run after code review. Measured time includes source generation, all kernels,
saving, HTML export and loaded-model replay. Supply an independently measured
conservative allowance for real-file preparation; the invented route does not
pretend to benchmark the imported gzip parser or acquisition data.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from neuro.notebook_inputs import demo_configuration
from neuro.place195 import file_hash


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--runtime-python", type=Path, default=Path(sys.executable))
    parser.add_argument("--dependency-path", action="append", default=[])
    parser.add_argument("--iterations", type=int, choices=(100, 1000), default=1000)
    parser.add_argument(
        "--real-preparation-seconds",
        type=float,
        required=True,
        help="Conservative aggregate allowance across all three real notebook reconstructions",
    )
    args = parser.parse_args()
    if not 0 <= args.real_preparation_seconds < 5400:
        raise ValueError("declare a finite nonnegative real preparation allowance")
    os.umask(0o077)
    args.output.mkdir(mode=0o700, parents=True, exist_ok=False)
    config = demo_configuration()
    config.update(
        landmarks=list(range(1, 7)),
        demo_units=27,
        demo_blocks=10,
        demo_bins=10,
        demo_train_sources_per_pool=5,
        demo_development_sources_per_pool=2,
    )
    config["execution"].update(
        iterations=args.iterations,
        train_rows_per_condition=16,
        development_rows_per_condition=8,
        batch_size=256,
    )
    manifest = args.output / "invented-benchmark-configuration.json"
    manifest.write_text(json.dumps(config, sort_keys=True, indent=2))
    command = [
        sys.executable,
        str(Path(__file__).with_name("execute_fresh_notebooks.py")),
        "--output",
        str(args.output / "run"),
        "--manifest",
        str(manifest),
        "--manifest-sha256",
        file_hash(manifest),
        "--runtime-python",
        str(args.runtime_python),
        "--timeout-seconds",
        "5400",
        "--memory-gib",
        "6",
    ]
    for path in args.dependency_path:
        command.extend(["--dependency-path", path])
    started = time.monotonic()
    subprocess.run(command, check=True)
    elapsed = time.monotonic() - started
    # Scaling the WHOLE measured workflow (not just optimizer time) is deliberately
    # conservative for a 100-update calibration; no biological extrapolation claim.
    projected = (
        elapsed * (1000 / args.iterations) + args.real_preparation_seconds
    ) * 1.25
    run_receipt = json.loads((args.output / "run/receipt.json").read_text())
    resources = json.loads((args.output / "run/resources.json").read_text())
    receipt = {
        "shape": {"units": 27, "bins": 10, "train_rows": 480, "development_rows": 240},
        "measured_seconds": elapsed,
        "calibration_iterations": args.iterations,
        "real_preparation_allowance_seconds": args.real_preparation_seconds,
        "projection_with_25_percent_headroom_seconds": projected,
        "within_90_minutes": projected < 5400,
        "fit_counts": run_receipt["fit_counts"],
        "resources": resources,
        "limit": "invented numerical shapes; real parser/preparation allowance is supplied, not inferred",
    }
    path = args.output / "benchmark-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True))
    path.chmod(0o600)
    if not receipt["within_90_minutes"]:
        raise RuntimeError("full-grid projection exceeds frozen deadline")
    print(
        "Shape-matched full-grid benchmark and conservative deadline projection passed."
    )


if __name__ == "__main__":
    main()
