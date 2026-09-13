#!/usr/bin/env python3
"""Check shipped bytes/presentation without local data, CEBRA, fitting or network.

Run from any directory with normal Python (not -O). This is a package consistency
check, not independent reconstruction of the scientific metrics from trials.
"""

import csv
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path


class ReportParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.current = None
        self.ids = []
        self.references = []
        self.figures = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        assert tag not in {"script", "iframe", "link", "object", "embed"}, tag
        assert not any(key.startswith("on") for key in attrs), "event handler"
        for key, value in attrs.items():
            if key in {"src", "srcset", "href", "xlink:href"} and tag != "a":
                assert value and value.startswith(("#", "data:")), f"{tag}:{key}"
            if value and key in {"href", "xlink:href"} and value.startswith("#"):
                self.references.append(value[1:])
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "svg":
            self.figures += 1
        if tag == "table":
            assert self.current is None, "unexpected nested table"
            self.current = []

    def handle_endtag(self, tag):
        if tag == "table":
            assert self.current is not None
            self.tables.append(re.sub(r"\s+", " ", "".join(self.current)).strip())
            self.current = None

    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)


def check():
    root = Path(__file__).resolve().parents[1]
    package = root / "docs/professor_updates/path_generalization_20260907"
    files = 0
    for line in (package / "SHA256SUMS").read_text().splitlines():
        expected, name = line.split("  ", 1)
        path = (root / name).resolve()
        assert path.is_relative_to(root), "checksum path outside repository"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
        files += 1
    assert files > 0
    name = "path-generalization-teaching-audit-20260907.html"
    current_text = (package / name).read_text()
    old = ReportParser()
    old.feed((package / "archive/release-20260907" / name).read_text())
    current = ReportParser()
    current.feed(current_text)
    assert current.tables == old.tables and len(current.tables) == 9
    assert current.figures == old.figures == 12
    assert len(current.ids) == len(set(current.ids)), "duplicate HTML/SVG IDs"
    refs = current.references + re.findall(r"url\(#([^)]*)\)", current_text)
    assert set(refs) <= set(current.ids), "unresolved internal reference"
    assert "old absent, edge elsewhere" not in current_text
    assert "<!-- no selected edge -->" in current_text
    with (package / "evidence/target_semantics/target_semantics_route_counts.csv").open(
        newline=""
    ) as handle:
        routes = list(csv.DictReader(handle))
    route = next(row for row in routes if row["source_count"] == "99")
    assert route["semantic_bucket"] == "old_absent_never_component"
    assert "D_N_R_T__N_R_M" not in route["route_signature"].split(">")
    try:
        audit = json.loads(
            (package / "evidence/audits/track_b_exact_audit.json").read_text()
        )
        manifest = json.loads((package / "report-manifest.json").read_text())
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Unreadable package evidence: {exc}") from exc
    assert audit["family_max_pvalue_exact"] == "19/21"
    assert hashlib.sha256((package / name).read_bytes()).hexdigest() == manifest[
        "report_sha256"
    ]
    return {"status": "verified", "files": files, "unchanged_tables": 9, "figures": 12}


if __name__ == "__main__":
    if not __debug__:
        raise SystemExit("Run without -O: verification uses assertions.")
    print(json.dumps(check(), indent=2))
