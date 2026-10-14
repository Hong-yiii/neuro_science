#!/usr/bin/env python3
"""Check a manuscript and package existing report images for offline use."""

import argparse
import base64
import os
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
# Source URLs retain their historical base so pinned Git citations stay truthful.
SOURCE_BASE = ROOT / "docs/reports/cebra-retrospective-20261012"
OUTPUT = ROOT / "outputs/cebra-retrospective-20261012/manuscript.html"
EVIDENCE_REVISION = "4862267"
REPOSITORY = "https://github.com/Hong-yiii/neuro_science"


class PageCheck(HTMLParser):
    """Small regression check: unique IDs, resolvable navigation, image alt text."""

    def __init__(self):
        super().__init__()
        self.ids = set()
        self.anchors = []
        self.images = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                raise ValueError(f"Duplicate ID: {attrs['id']}")
            self.ids.add(attrs["id"])
        href = attrs.get("href") or ""
        if tag == "a" and href.startswith("#"):
            self.anchors.append(href[1:])
        if tag == "img":
            if not attrs.get("alt") or not attrs.get("src"):
                raise ValueError(
                    "Every evidence image needs src and meaningful alt text"
                )
            self.images += 1

    def check(self, text):
        self.feed(text)
        self.close()
        missing = set(self.anchors) - self.ids
        if missing or not self.images:
            raise ValueError(f"Broken anchors {missing}, image count {self.images}")


class ImageSources(HTMLParser):
    """Locate existing embedded images without executing a historical report."""

    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.sources.append(dict(attrs).get("src") or "")


def image_bytes(target, fragment):
    if target.suffix == ".png" and not fragment:
        data = target.read_bytes()
    elif target.suffix == ".html" and re.fullmatch(r"image-(0|[1-9][0-9]*)", fragment):
        images = ImageSources()
        images.feed(target.read_text(encoding="utf-8"))
        try:
            index = int(fragment.removeprefix("image-"))
        except ValueError as exc:
            raise ValueError(f"Invalid embedded-image index: {target}") from exc
        if index >= len(images.sources):
            raise ValueError(f"Missing image {index}: {target}")
        prefix = "data:image/png;base64,"
        if not images.sources[index].startswith(prefix):
            raise ValueError(f"Expected an embedded PNG at image {index}: {target}")
        data = base64.b64decode(images.sources[index][len(prefix) :], validate=True)
    else:
        raise ValueError(
            f"Expected a PNG or historical HTML#image-N: {target}#{fragment}"
        )
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError(f"Invalid PNG: {target}")
    return data


def standalone(source):
    PageCheck().check(source)

    def replace(match):
        attribute, url = match.groups()
        if url.startswith("#"):
            return match.group()
        parsed = urlsplit(url)
        if (
            attribute == "href"
            and parsed.scheme == "https"
            and parsed.netloc == "doi.org"
            and parsed.path.startswith("/10.")
            and not parsed.query
            and not parsed.fragment
        ):
            return match.group()
        if parsed.scheme or parsed.netloc or parsed.query:
            raise ValueError(f"Expected a repository-local source reference: {url}")
        target = Path(os.path.abspath(SOURCE_BASE / parsed.path))
        target.resolve().relative_to(ROOT)  # reject escaping symlink targets
        relative = target.relative_to(ROOT).as_posix()
        if not target.is_file():
            raise ValueError(f"Missing source: {relative}")
        subprocess.run(
            ["git", "cat-file", "-e", f"{EVIDENCE_REVISION}:{relative}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        if attribute == "src":
            data = image_bytes(target, parsed.fragment)
            url = "data:image/png;base64," + base64.b64encode(data).decode("ascii")
        else:
            url = f"{REPOSITORY}/blob/{EVIDENCE_REVISION}/{quote(relative)}"
            if parsed.fragment:
                url += "#" + quote(parsed.fragment)
        return f'{attribute}="{url}"'

    # ponytail: double-quoted attributes in this owned template, not a general HTML bundler.
    result = re.sub(r'\b(src|href)="([^"]+)"', replace, source)
    PageCheck().check(result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source",
        nargs="?",
        default="manuscript.html",
        choices=("outline.html", "manuscript.html"),
    )
    filename = parser.parse_args().source
    page = standalone((HERE / filename).read_text(encoding="utf-8"))
    output = OUTPUT.with_name(filename)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")
    print(f"Checked anchors, images and pinned evidence paths; wrote {output}")
