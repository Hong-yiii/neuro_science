"""Run directly: python3 report/test_build.py (includes exact frozen integrity)."""

import base64
import os
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from build import HERE, SOURCE_BASE, image_bytes, standalone


def rejects(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Invalid manuscript input was accepted")


def check_frozen():
    frozen = (HERE / "retrospective-frozen-20261012.html").read_bytes()
    assert sha256(frozen).hexdigest() == (
        "86497662096908f5fa92f1d00747377b2046e07a37ea225ae8fdbedcc9dfbde6"
    ), "The frozen reading milestone must not be overwritten"


def check_builder():
    image = "../cebra-endpoint-time-readout-20261006/figures/wholecue_log_loss.png"
    image_path = Path(os.path.abspath(SOURCE_BASE / image))
    png = image_path.read_bytes()
    with TemporaryDirectory(prefix="neuro-manuscript-check-") as directory:
        report = Path(directory) / "source.html"
        report.write_text(
            '<img src="https://example.com/not-local.png">'
            '<img src="data:image/png;base64,'
            + base64.b64encode(png).decode("ascii")
            + '">',
            encoding="utf-8",
        )
        assert image_bytes(image_path, "") == png
        assert image_bytes(report, "image-1") == png
        for fragment in ("image-0", "image-2", "image--1", "image-01", "wrong"):
            rejects(lambda fragment=fragment: image_bytes(report, fragment))
        report.write_text('<img src="data:image/png;base64,not-base64">')
        rejects(lambda: image_bytes(report, "image-0"))
        rejects(lambda: image_bytes(image_path, "image-0"))

    source = f'<h1 id="title">Draft</h1><img src="{image}" alt="Loss"><a href="#title">Top</a>'
    doi = '<a href="https://doi.org/10.1038/s41586-023-06031-6">CEBRA</a>'
    result = standalone(source + doi)
    assert 'src="data:image/png;base64,' in result
    assert doi in result
    linked = standalone(
        source
        + '<a href="../cebra-endpoint-time-readout-20261006/report.html">Evidence</a>'
    )
    assert (
        "/blob/4862267/docs/reports/cebra-endpoint-time-readout-20261006/report.html"
        in linked
    )
    for bad in (
        source.replace('href="#title"', 'href="#missing"'),
        source + '<p id="title">Duplicate</p>',
        source.replace('alt="Loss"', 'alt=""'),
        source.replace(image, "https://doi.org/10.1038/s41586-023-06031-6"),
        source + '<a href="https://doi.org@evil.example/10.123/x">No</a>',
        source + '<a href="http://doi.org/10.123/x">No</a>',
    ):
        rejects(lambda bad=bad: standalone(bad))
    print(
        "PASS: image bytes/indexing, invalid inputs, anchors, alt text, DOI and historical evidence links"
    )


if __name__ == "__main__":
    check_builder()
    check_frozen()
    print("PASS: exact frozen report checksum")
