"""Check the current editorial slice using tracked aggregates only; stdlib, no fits.

Run: /usr/bin/python3 -B report/test_editorial.py
"""

import base64
import csv
import io
import math
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from statistics import mean

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


class MetricDownload(HTMLParser):
    def __init__(self):
        super().__init__()
        self.downloads = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("download") == "endpoint_experiment_metrics.csv":
            self.downloads.append(attrs["href"])


def check_checkpoints(source):
    page = MetricDownload()
    page.feed(
        (
            ROOT
            / "docs/professor_updates/start_goal_20260907/endpoint-research-report.html"
        ).read_text()
    )
    assert len(page.downloads) == 1
    header, body = page.downloads[0].split(",", 1)
    assert header == "data:text/csv;base64"
    rows = [
        row
        for row in csv.DictReader(
            io.StringIO(base64.b64decode(body, validate=True).decode())
        )
        if row["case"] == "time_t1" and row["target"] == "joint"
    ]
    expected = {
        (split, str(step), str(seed))
        for split in ("train", "development")
        for step in (250, 1000, 3000)
        for seed in range(3)
    }
    assert len(rows) == 18
    assert {(r["split"], r["step"], r["seed"]) for r in rows} == expected
    for row in rows:
        assert (row["phase"], row["decoder"], row["decoder_C"]) == (
            "cebra",
            "logistic",
            "0.01",
        )
        assert (row["dim"], row["features"], row["temperature"]) == ("8", "80", "1")
        assert row["n_rows"] == ("480" if row["split"] == "train" else "240")

    svgs = [ET.fromstring(s) for s in re.findall(r"<svg\b.*?</svg>", source, re.S)]
    panels = [p for svg in svgs for p in svg.findall(".//*[@data-checkpoint-split]")]
    keys = {(split, step) for split, step, _ in expected}
    assert len(panels) == len(keys) == 6
    assert {
        (p.attrib["data-checkpoint-split"], p.attrib["data-step"]) for p in panels
    } == keys
    coordinates = {}
    for panel in panels:
        split, step = panel.attrib["data-checkpoint-split"], panel.attrib["data-step"]
        values = [
            float(r["accuracy"])
            for r in rows
            if (r["split"], r["step"]) == (split, step)
        ]
        (label,) = panel.findall("text")
        (point,) = panel.findall("circle")
        (span,) = panel.findall("line")
        assert (label.text or "").strip() == f"{100 * mean(values):.2f}%", (split, step)
        x, y = 80 + 0.2 * int(step), 300 - 240 * mean(values)
        for actual, wanted in (
            (point.attrib["cx"], x),
            (point.attrib["cy"], y),
            (span.attrib["x1"], x),
            (span.attrib["x2"], x),
            (span.attrib["y1"], 300 - 240 * max(values)),
            (span.attrib["y2"], 300 - 240 * min(values)),
        ):
            assert math.isclose(float(actual), wanted, abs_tol=1e-6), (split, step)
        coordinates[split, int(step)] = (x, y)
    lines = [p for svg in svgs for p in svg.findall(".//*[@data-checkpoint-line]")]
    assert len(lines) == 2
    assert {p.attrib["data-checkpoint-line"] for p in lines} == {"train", "development"}
    for line in lines:
        split = line.attrib["data-checkpoint-line"]
        points = [
            tuple(map(float, p.split(","))) for p in line.attrib["points"].split()
        ]
        assert len(points) == 3
        for step, point in zip((250, 1000, 3000), points, strict=True):
            assert all(
                math.isclose(a, b, abs_tol=1e-6)
                for a, b in zip(point, coordinates[split, step], strict=True)
            )


def check_endpoint_table(source):
    tables = [ET.fromstring(s) for s in re.findall(r"<table>.*?</table>", source, re.S)]
    (table,) = [
        t
        for t in tables
        if "Latest whole-cue endpoint comparison" in "".join(t.itertext())
    ]
    headings = ["".join(h.itertext()).strip() for h in table.findall("./thead/tr/th")]
    assert headings == ["Representation/readout", "Pair BA", "Start BA", "Goal BA"]
    with (
        ROOT
        / "docs/reports/cebra-endpoint-time-readout-20261006/tables/observed_metrics_by_seed.csv"
    ).open(newline="") as stream:
        rows = [
            r
            for r in csv.DictReader(stream)
            if r["window"] == "wholecue" and r["split"] == "development"
        ]
    models = ("raw", "pca8", "cebra_cue", "cebra_joint", "raw_svd_lda")
    labels = (
        "Raw + logistic",
        "PCA8/bin + logistic",
        "Cue-only CEBRA-Time + logistic",
        "Joint CEBRA-Time + logistic",
        "Raw SVD-LDA",
    )
    displays = table.findall("./tbody/tr")
    assert len(displays) == len(models) == 5
    for display, model, label in zip(displays, models, labels, strict=True):
        cells = ["".join(c.itertext()).strip() for c in display.findall("td")]
        assert len(cells) == 4 and cells[0] == label
        for target, value in zip(("pair30", "start6", "goal6"), cells[1:], strict=True):
            selected = [
                r for r in rows if (r["representation"], r["target"]) == (model, target)
            ]
            assert len(selected) == 3 and {r["seed"] for r in selected} == {
                "0",
                "1",
                "2",
            }
            assert (
                value
                == f"{100 * mean(float(r['balanced_accuracy']) for r in selected):.2f}%"
            )


def main():
    source = (HERE / "manuscript.html").read_text()
    assert source.index('id="training-validation"') < source.index('id="results"')
    for removed in (
        "wholecue_log_loss.png",
        "null_families.png",
        'id="fig-path-nulls"',
        "Figure 8",
        "Figure S6",
    ):
        assert removed not in source, removed
    assert "Original probability-loss selection and success criteria" in source
    prose = " ".join(source.split())
    assert "within a bin" in prose and "not be relabeled as neural variability" in prose
    check_checkpoints(source)
    check_endpoint_table(source)
    print(
        "PASS: historical 18-row checkpoint contract, six means/ranges/coordinates, 15 endpoint BA scores and editorial boundaries"
    )


if __name__ == "__main__":
    main()
