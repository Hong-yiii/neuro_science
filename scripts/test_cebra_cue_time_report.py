"""Artifact QA: run after rendering the accepted cue-time report (no model imports)."""

import base64
import csv
import hashlib
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/cebra-cue-time-readout-20261005"


class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.links = []
        self.executable_assets = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "img":
            self.images.append(attrs)
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])
        if tag in ("script", "iframe", "link"):
            self.executable_assets.append(attrs)


class CueTimeReportTest(unittest.TestCase):
    def test_final_geometry_against_saved_embeddings_without_producer_helpers(self):
        accepted = (
            ROOT
            / "outputs/cebra-full-trial-transfer-20260924/biological-run-20260924T162913Z/worlds/00_observed"
        )
        with (REPORT / "geometry_spectra.csv").open() as stream:
            rows = list(csv.DictReader(stream))
        checked = 0
        for seed in range(3):
            for arm in ("cue_time", "full_time"):
                with np.load(
                    accepted / f"seed{seed}/encoders/{arm}/cue_embeddings.npz",
                    allow_pickle=False,
                ) as saved:
                    for split in ("train", "validation"):
                        z = saved[f"Z_{split}"].astype(float)
                        for window in (
                            "wholecue80",
                            *[f"bin{b:02d}_8d" for b in range(10)],
                        ):
                            x = (
                                z
                                if window == "wholecue80"
                                else z.reshape(len(z), 10, 8)[:, int(window[3:5])]
                            )
                            centered = x - x.mean(axis=0)
                            gram = centered.T @ centered
                            # Independent covariance identity, rather than producer SVD helper.
                            participation = np.trace(gram) ** 2 / np.sum(gram**2)
                            row = next(
                                r
                                for r in rows
                                if r["seed"] == str(seed)
                                and r["arm"] == arm
                                and r["checkpoint_step"] == "1000"
                                and r["split"] == split
                                and r["space"] == window
                            )
                            self.assertAlmostEqual(
                                float(row["participation_ratio"]),
                                participation,
                                places=4,
                            )
                            self.assertAlmostEqual(
                                sum(json.loads(row["variance_fractions"])),
                                1.0,
                                places=5,
                            )
                            checked += 1
        self.assertEqual(checked, 132)

    def test_verified_self_contained_report_and_numeric_exports(self):
        html = (REPORT / "report.html").read_bytes()
        parser = Assets()
        parser.feed(html.decode())
        self.assertEqual(len(parser.images), 16)
        self.assertFalse(parser.executable_assets)
        for image in parser.images:
            self.assertTrue(image.get("alt"))
            prefix, encoded = image["src"].split(",", 1)
            self.assertEqual(prefix, "data:image/png;base64")
            self.assertTrue(
                base64.b64decode(encoded, validate=True).startswith(
                    b"\x89PNG\r\n\x1a\n"
                )
            )
        for link in parser.links:
            self.assertFalse(link.startswith(("http:", "https:", "//")))
            if not link.startswith("#"):
                self.assertTrue((REPORT / link.split("#", 1)[0]).is_file(), link)
        receipt = json.loads((REPORT / "render_receipt.json").read_text())
        self.assertEqual(receipt["html_sha256"], hashlib.sha256(html).hexdigest())
        self.assertEqual(receipt["fit_calls"], 0)
        verified = json.loads((REPORT / "verification.json").read_text())
        self.assertEqual(verified["status"], "verified")
        self.assertEqual(verified["new_single_bin_readouts_checked"], 5040)
        self.assertEqual(verified["wholecue_replays_checked"], 504)
        with (REPORT / "observed_means.csv").open() as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 88)
        self.assertEqual(
            len({(r["representation"], r["readout"], r["window"]) for r in rows}), 88
        )
        for row in rows:
            seeds = json.loads(row["balanced_accuracy_seeds"])
            self.assertEqual(len(seeds), 3)
            self.assertAlmostEqual(float(row["balanced_accuracy"]), sum(seeds) / 3)
        for rep, window, expected in (
            ("full_time", "bin01", 8 / 9),
            ("full_time", "wholecue", 89 / 144),
            ("raw290", "bin02", 17 / 18),
        ):
            row = next(
                r
                for r in rows
                if (r["representation"], r["readout"], r["window"])
                == (rep, "logistic", window)
            )
            self.assertAlmostEqual(float(row["balanced_accuracy"]), expected)
        with (REPORT / "observed_confusions.csv").open() as stream:
            confusion = list(csv.DictReader(stream))
        self.assertEqual(len(confusion), 4 * 2 * 11 * 3 * 4)
        for row in confusion:
            self.assertEqual(
                int(row["true_class_support"]),
                24 if row["true_label"] == "absent" else 6,
            )
            self.assertAlmostEqual(
                float(row["true_class_normalized"]),
                int(row["count"]) / int(row["true_class_support"]),
            )


if __name__ == "__main__":
    unittest.main()
