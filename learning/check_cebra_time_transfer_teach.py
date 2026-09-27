"""Check the standalone lesson against the committed result receipt; never fit models.

Run: python3 learning/check_cebra_time_transfer_teach.py
"""
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LESSON = ROOT / "learning/cebra-time-transfer-teach-max-20260925.html"
RESULTS = ROOT / "docs/reports/cebra-full-trial-transfer/summary.json"


class LessonParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.references = []
        self.metrics = []
        self.cell = None
        self.diagrams = 0
        self.captions = 0

    def handle_starttag(self, tag, attrs):
        a = {name: value or "" for name, value in attrs}
        assert tag not in {"script", "iframe", "object", "embed", "link", "base", "form"}, tag
        for name in ("src", "srcset", "poster"):
            if a.get(name):
                assert a[name].startswith("data:"), (tag, name, a[name])
        assert not any(name.startswith("on") for name in a), "unexpected event handler"
        if a.get("id"):
            assert a["id"] not in self.ids, f"duplicate id: {a['id']}"
            self.ids.add(a["id"])
        if a.get("href", "").startswith("#"):
            self.references.append(a["href"][1:])
        if tag == "svg":
            assert a.get("role") == "img" and a.get("aria-labelledby")
            self.references.extend(a["aria-labelledby"].split())
            self.diagrams += 1
        if tag == "figcaption":
            self.captions += 1
        if a.get("data-key"):
            assert tag == "td" and self.cell is None
            self.cell = [a["data-key"], a.get("data-percent") == "true", ""]

    def handle_data(self, data):
        if self.cell is not None:
            self.cell[2] += data

    def handle_endtag(self, tag):
        if tag == "td" and self.cell is not None:
            self.metrics.append(self.cell)
            self.cell = None


def check():
    html = LESSON.read_text()
    assert '<html lang="en">' in html and 'name="viewport"' in html
    assert not re.search(r"@import", html, re.IGNORECASE)
    parser = LessonParser()
    parser.feed(html)
    required = {"what-i-understand", "system-diagram", "objective", "source-map", "story", "review-notes", "teach-back"}
    assert required <= parser.ids and set(parser.references) <= parser.ids
    for target in re.findall(r"url\(([^)]+)\)", html):
        fragment = target.strip().strip("\"'")
        assert fragment.startswith("#") and fragment[1:] in parser.ids
    assert parser.diagrams == parser.captions == 4
    assert len(parser.metrics) == 18
    observed = json.loads(RESULTS.read_text())["observed"]
    for key, percent, text in parser.metrics:
        group, field = key.split(":")
        shown = text.strip().removesuffix("%")
        expected = observed[group][field] * (100 if percent else 1)
        precision = len(shown.split(".")[1]) if "." in shown else 0
        assert math.isclose(float(shown), expected, rel_tol=0, abs_tol=0.50001 * 10 ** -precision), (key, text, expected)
    assert "not confidence intervals" in html and "No such follow-up was run" in html
    assert "rm -- /tmp/pi-teach/20260925T134330Z-cebra-time-transfer-max.html" in html
    print(f"PASS: {len(parser.metrics)} metric cells, {parser.diagrams} accessible inline diagrams, anchors and offline-resource checks; zero fits")


if __name__ == "__main__":
    check()
