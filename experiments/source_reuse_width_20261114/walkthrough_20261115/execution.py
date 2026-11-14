"""Own the visible first case, then complete the unchanged bounded schedule."""

from __future__ import annotations

import csv
import gc
import json
from contextlib import contextmanager
from pathlib import Path

from .. import study
from .staging import StagedCase


class PartExecution:
    def __init__(self, data, meta, config, root, part):
        if config != study.configuration(config["design"]):
            raise ValueError("configuration differs from the frozen study")
        self.data, self.meta, self.config = data, meta, config
        self.root, self.part = Path(root), part
        arms = study.PART_ARMS[part] if part == "reuse" else ("Wmid", "Wfull")
        self.selected = [c for c in study.schedule() if c["arm"] in arms]
        self.first = self.selected[0]
        self.aggregate = self.root / ("aggregates_" + part)
        self.aggregate.mkdir(mode=0o700)
        self.results = {
            k: [] for k in ("metrics", "confusions", "learning", "trajectories")
        }
        self.streamed = (
            "source_usage",
            "pool_usage",
            "source_errors",
            "class_errors",
            "overlap",
        )
        self.handles, self.writers, self.attempts = {}, {}, []
        self.accounting = study.GridFitAccounting(cebra=True).start()
        self.closed = False
        self.staged = None
        self.stage_number = 0

    def log(self):
        with (self.root / "attempt-log.jsonl").open("a") as handle:
            handle.write(json.dumps(self.attempts[-1]) + "\n")

    def start(self, case):
        print("Fitting", case["id"], flush=True)
        self.attempts.append({**case, "status": "started"})
        self.log()

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.actual = self.accounting.stop()
        study.write_json(
            self.root / ("actual-fit-counts-" + self.part + ".json"), self.actual
        )
        for handle in self.handles.values():
            handle.close()

    @contextmanager
    def stage(self, label):
        """Persist partial accounting and failure before propagating any cell error."""
        if self.closed:
            raise ValueError("execution already closed; no retry permitted")
        try:
            yield
            self.stage_number += 1
            study.write_json(
                self.root / f"stage-{self.part}-{self.stage_number:02d}.json",
                dict(
                    label=label,
                    completed=True,
                    actual_fit_counts=dict(self.accounting.counts),
                    attempts=self.attempts,
                ),
            )
        except BaseException as exc:
            if self.attempts and self.attempts[-1]["status"] == "started":
                self.attempts[-1].update(status="failed", exception=type(exc).__name__)
                self.log()
            self.close()
            study.write_json(
                self.root / ("failure_" + self.part + ".json"),
                dict(
                    stage=label,
                    exception=type(exc).__name__,
                    message=str(exc),
                    attempts=self.attempts,
                    actual_fit_counts=self.actual,
                ),
            )
            raise

    def begin(self, plans):
        if self.staged is not None or self.attempts:
            raise ValueError("first case already started")
        with self.stage("materialize first case"):
            self.start(self.first)
            self.staged = StagedCase(
                self.first,
                *plans[self.first["arm"]],
                meta=self.meta,
                config=self.config,
                run_root=self.root,
            )
        return self.staged

    def collect(self, result):
        for name in self.streamed:
            values = result[name]
            if name not in self.handles:
                self.handles[name] = (self.aggregate / (name + ".csv")).open(
                    "x", newline=""
                )
                self.writers[name] = csv.DictWriter(
                    self.handles[name], fieldnames=list(values[0])
                )
                self.writers[name].writeheader()
            self.writers[name].writerows(values)
            self.handles[name].flush()
        for name in self.results:
            value = result[name]
            self.results[name].extend(value if isinstance(value, list) else [value])
        self.attempts[-1]["status"] = "completed"
        self.log()

    def finish_remaining(self):
        """Close the first case once, then fit only the remaining scheduled cases."""
        with self.stage("finish bounded schedule"):
            self.collect(self.staged.finish())
            self.staged = None
            previous = None
            for case in self.selected[1:]:
                key = case["world"], case["seed"]
                if key != previous:
                    permutation = None if key[0] == "observed" else int(key[0][8:])
                    plans = study.paired_plans(
                        self.data,
                        self.meta,
                        self.config["design"],
                        seed=key[1],
                        permutation=permutation,
                    )
                    study.verify_plans(plans)
                    previous = key
                self.start(case)
                self.collect(
                    study.train_case(
                        case,
                        *plans[case["arm"]],
                        meta=self.meta,
                        config=self.config,
                        run_root=self.root,
                    )
                )
                gc.collect()
            for name, values in self.results.items():
                if name == "metrics":
                    study.write_csv(self.aggregate / (name + ".csv"), values)
                else:
                    study.write_json(self.aggregate / (name + ".json"), values)
            study.write_json(
                self.root / ("attempts_" + self.part + ".json"), self.attempts
            )
            study.write_json(
                self.root / ("fit-counts-after-" + self.part + ".json"),
                dict(self.accounting.counts),
            )
            expected = {
                k: v * len(self.selected) // 48
                for k, v in self.config["expected_fit_counts"].items()
            }
            if self.accounting.counts != expected:
                raise ValueError("actual fit accounting differs from bounded schedule")
        self.close()
        return self.results
