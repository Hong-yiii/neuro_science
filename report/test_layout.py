"""Small relocation check: tracked reading bytes, legacy paths and weekly links.

Run from any directory: python3 /path/to/repo/report/test_layout.py
No scientific imports or private inputs.
"""

import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


class LocalResources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"src", "href"} and value:
                url = urlsplit(value)
                if not url.scheme and not url.netloc and url.path:
                    self.paths.append(url.path)


def main():
    records = json.loads((ROOT / "history/relocations.json").read_text())["files"]
    assert len(records) == len({r["current"] for r in records}) == 11
    for record in records:
        old, new = ROOT / record["original"], ROOT / record["current"]
        assert old.is_symlink() and old.resolve() == new.resolve(), old
        assert hashlib.sha256(new.read_bytes()).hexdigest() == record["sha256"], new
        page = LocalResources()
        page.feed(new.read_text())
        for path in page.paths:
            assert (new.parent / path).is_file(), (new, path)
    weeks = sorted((ROOT / "history").glob("week-*/README.md"))
    assert len(weeks) == 7
    for page in [
        ROOT / "README.md",
        ROOT / "report/README.md",
        ROOT / "history/README.md",
        *weeks,
    ]:
        for href in re.findall(r"\]\(([^)]+)\)", page.read_text()):
            url = urlsplit(href)
            if not url.scheme and not url.netloc and url.path:
                assert (page.parent / url.path).exists(), (page, href)
    assert (
        ROOT / "docs/reports/cebra-retrospective-20261012"
    ).resolve() == ROOT / "report"
    print(
        "PASS: 11 byte-preserved reading moves, legacy aliases, seven weekly overviews and current navigation"
    )


if __name__ == "__main__":
    main()
