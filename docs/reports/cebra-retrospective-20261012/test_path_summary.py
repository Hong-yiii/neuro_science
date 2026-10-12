"""Check manuscript tables/diagrams against tracked aggregate CSVs; no model access.

Run: /usr/bin/python3 docs/reports/cebra-retrospective-20261012/test_path_summary.py
"""

import csv
import json
import math
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent / "cebra-cue-time-readout-20261005"


class ScoreCells(HTMLParser):
    def __init__(self):
        super().__init__()
        self.model = None
        self.readout = None
        self.text = []
        self.values = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "tr":
            self.model = attrs.get("data-path-score")
        if tag == "td":
            self.readout = attrs.get("data-readout")
            self.text = []

    def handle_data(self, data):
        if self.model and self.readout:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == "td" and self.model and self.readout:
            key = (self.model, self.readout)
            assert key not in self.values, key
            self.values[key] = "".join(self.text).strip()
            self.readout = None
        if tag == "tr":
            self.model = None


def main():
    source = (HERE / "manuscript.html").read_text()
    with (EVIDENCE / "observed_means.csv").open(newline="") as stream:
        means = {
            (row["representation"], row["readout"]): row
            for row in csv.DictReader(stream)
            if row["window"] == "wholecue"
        }
    table = ScoreCells()
    table.feed(source)
    assert len(means) == 8 and table.values.keys() == means.keys()
    for key, value in table.values.items():
        assert value == f"{100 * float(means[key]['balanced_accuracy']):.2f}%", key

    with (EVIDENCE / "observed_confusions.csv").open(newline="") as stream:
        confusions = [
            row
            for row in csv.DictReader(stream)
            if row["world"] == "observed"
            and row["window"] == "wholecue"
            and row["readout"] == "logistic"
            and row["representation"] in {"cue_time", "full_time"}
        ]
    assert len(confusions) == 24
    svgs = [
        ET.fromstring(fragment)
        for fragment in re.findall(r"<svg\b.*?</svg>", source, re.S)
    ]
    panels = [
        node for svg in svgs for node in svg.findall(".//*[@data-confusion-model]")
    ]
    assert len(panels) == 6
    assert {
        (p.attrib["data-confusion-model"], p.attrib["data-seed"]) for p in panels
    } == {
        (model, str(seed)) for model in ("cue_time", "full_time") for seed in range(3)
    }
    for panel in panels:
        model, seed = panel.attrib["data-confusion-model"], panel.attrib["data-seed"]
        rows = [
            row
            for row in confusions
            if row["representation"] == model and row["seed"] == seed
        ]
        expected = {f"{r['true_label']},{r['predicted_label']}": r for r in rows}
        for attribute, column, percent in [
            ("data-cell", "count", False),
            ("data-recall", "true_class_normalized", True),
        ]:
            cells = panel.findall(f".//*[@{attribute}]")
            assert (
                len(cells) == 4
                and {c.attrib[attribute] for c in cells} == expected.keys()
            )
            for cell in cells:
                value = expected[cell.attrib[attribute]][column]
                display = f"{100 * float(value):.1f}%" if percent else value
                assert "".join(cell.itertext()).strip() == display, (
                    model,
                    seed,
                    column,
                )
        counts = {key: int(row["count"]) for key, row in expected.items()}
        assert counts["absent,absent"] + counts["absent,present"] == 24
        assert counts["present,absent"] + counts["present,present"] == 6
        ba = (counts["absent,absent"] / 24 + counts["present,present"] / 6) / 2
        assert math.isclose(
            ba,
            json.loads(means[model, "logistic"]["balanced_accuracy_seeds"])[int(seed)],
        )
        stats = {
            n.attrib["data-stat"]: "".join(n.itertext()).strip()
            for n in panel.findall(".//*[@data-stat]")
        }
        assert stats["ba"] == f"BA: {100 * ba:.2f}%"
        assert (
            stats["predicted-absent"]
            == f"Predicted absent: {counts['absent,absent'] + counts['present,absent']}/30"
        )

    recalls = [node for svg in svgs for node in svg.findall(".//*[@data-mean-model]")]
    assert len(recalls) == 3
    assert {p.attrib["data-mean-model"] for p in recalls} == {
        "cue_time",
        "full_time",
        "always_absent",
    }
    for panel in recalls:
        model = panel.attrib["data-mean-model"]
        values = (
            {"absent": 1.0, "present": 0.0, "ba": 0.5}
            if model == "always_absent"
            else {
                "absent": float(means[model, "logistic"]["recall_absent"]),
                "present": float(means[model, "logistic"]["recall_present"]),
                "ba": float(means[model, "logistic"]["balanced_accuracy"]),
            }
        )
        assert math.isclose(values["ba"], (values["absent"] + values["present"]) / 2)
        labels = panel.findall(".//*[@data-mean]")
        bars = panel.findall(".//*[@data-bar]")
        assert len(labels) == 3 and len(bars) == 2
        for node in labels:
            assert (
                "".join(node.itertext()).strip()
                == f"{100 * values[node.attrib['data-mean']]:.2f}%"
            )
        for node in bars:
            assert math.isclose(
                float(node.attrib["width"]),
                330 * values[node.attrib["data-bar"]],
                abs_tol=1e-6,
            )
    print(
        "PASS: eight whole-cue scores; 24 confusion cells/recalls; six seed summaries; mean labels/bar lengths."
    )


if __name__ == "__main__":
    main()
