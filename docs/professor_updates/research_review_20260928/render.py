"""Build/check the offline professor review; no model/runtime imports or fitting."""

import html
import json
import math
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from statistics import mean

from diagrams import all_diagrams, number
from markdown_it import MarkdownIt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TARGET = HERE / "review.html"
REVISION = "fac639b016ca2dd435eed689f9d5544d7c636e96"
SUMMARY = ROOT / "docs/reports/cebra-full-trial-transfer/summary.json"
DOWNLOAD_JS = """
(() => {
  const button = document.getElementById('download-html');
  const status = document.getElementById('download-status');
  button.disabled = false;
  button.addEventListener('click', () => {
    try {
      const copy = document.documentElement.cloneNode(true);
      copy.querySelector('#download-status').textContent = '';
      copy.querySelector('#download-html').disabled = true;
      const blob = new Blob(['<!doctype html>\\n' + copy.outerHTML], {type:'text/html;charset=utf-8'});
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'research-review-20260928.html';
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 30000);
      status.textContent = 'Download requested — standalone HTML.';
    } catch (error) {
      status.textContent = 'Download failed; use your browser’s Save Page command.';
      console.error(error);
    }
  });
})();
"""


def check_numbers(summary: dict, text: str) -> None:
    """Check the published aggregate and rule arithmetic against saved evidence."""
    observed = summary["observed"]
    for arm in ("cue_time/logistic", "full_time/logistic"):
        row = observed[arm]
        for metric in ("balanced_accuracy", "auroc", "balanced_log_loss"):
            value = mean(number(seed[metric]) for seed in row["seed_rows"])
            assert math.isclose(value, number(row[metric]), abs_tol=1e-12)
            display = (f"{value * 100:.2f}%" if metric == "balanced_accuracy" else
                       f"{value:.3f}" if metric == "auroc" else f"{value:.6f}")
            assert display in text, f"Missing or stale displayed value: {display}"
    primary = summary["primary_and_nulls"]
    gain = number(observed["cue_time/logistic"]["balanced_log_loss"]) - number(observed["full_time/logistic"]["balanced_log_loss"])
    assert math.isclose(gain, primary["observed_time_logistic_mean_gain"], abs_tol=1e-12)
    assert f"{gain:.6f}" in text and f"{math.log(2):.6f}" in text
    assert primary["criteria"] == {
        "full_auroc_gt_0p5": observed["full_time/logistic"]["auroc"] > .5,
        "full_ba_gt_0p5": observed["full_time/logistic"]["balanced_accuracy"] > .5,
        "full_loss_lt_log2": observed["full_time/logistic"]["balanced_log_loss"] < math.log(2),
        "gain_ge_0p01": gain >= .01,
    }
    assert not all(primary["criteria"].values())
    for key in ("balanced_accuracy", "auroc"):
        value = number(observed["full_time/svc"][key])
        display = f"{value * 100:.2f}%" if key == "balanced_accuracy" else f"{value:.3f}".lstrip("0")
        assert display in text, f"Missing RBF result: {display}"
    # These source-backed headline comparisons must stay traceable to their study.
    for filename, values in {
        "start-goal-autoresearch.md": ["69.72%", "51.67%", "83.61%"],
        "start-goal-cebra-diagnosis.md": ["42.78%", "51.67%", "50.14%"],
        "cebra-decoder-autoresearch-20260924.md": ["24.92%", "37.33%", "42.92%", "77.50%"],
    }.items():
        evidence = (ROOT / "docs/reports" / filename).read_text()
        assert all(value in text and value in evidence for value in values), filename


class PageCheck(HTMLParser):
    """Check navigation and forbid external executable/asset dependencies."""

    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.fragments: list[str] = []
        self.headings = 0
        self.canvases = 0
        self.scripts = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        assert tag not in {"iframe", "link", "object", "embed", "base"}, tag
        assert not any(key.startswith("on") or key in {"src", "srcset"} for key in values), values
        if "id" in values:
            self.ids.append(str(values["id"]))
        href = values.get("href", "") or ""
        valid_href = href.startswith(("#", "https://github.com/Hong-yiii/neuro_science/blob/"))
        assert not href or valid_href, href
        if href.startswith("#"):
            self.fragments.append(href[1:])
        self.headings += tag == "h2"
        self.canvases += tag == "canvas"
        self.scripts += tag == "script"


def source_link(match: re.Match[str]) -> str:
    href, label = match.groups()
    if href.startswith("#"):
        return match.group(0)
    path = (HERE / href).resolve()
    assert path.is_file(), f"Missing cited source: {href}"
    relative = path.relative_to(ROOT)
    return f'<a href="https://github.com/Hong-yiii/neuro_science/blob/{REVISION}/{html.escape(relative.as_posix())}">{label}</a>'


def render() -> str:
    text = (HERE / "review.md").read_text()
    try:
        summary = json.loads(SUMMARY.read_text())
        payload_obj = json.loads((HERE / "payload.json").read_text())
        losses_obj = json.loads((HERE / "loss-curves.json").read_text())
    except (OSError, ValueError) as error:
        raise ValueError(f"Cannot read saved presentation evidence: {error}") from error
    check_numbers(summary, text)
    diagrams = all_diagrams(summary)
    for name, filename in (("ENDPOINT_LOSS", "endpoint-loss.svg"),
                           ("JOINT_LOSS", "joint-loss.svg")):
        diagrams[name] = '<figure class="diagram"><div class="chart-scroll" tabindex="0" role="region" aria-label="Saved encoder training losses">' + (HERE / filename).read_text() + '</div></figure>'
    diagrams["VIEWER"] = (HERE / "viewer.html").read_text()
    for key, content in diagrams.items():
        assert text.count(f"@@{key}@@") == 1, key
        text = text.replace(f"@@{key}@@", content)
    assert "@@" not in text, "Unresolved presentation placeholder"
    document = MarkdownIt("commonmark", {"html": True}).enable("table").render(text)
    document = re.sub(r"<h2>([1-7])\. (.*?)</h2>", r'<h2 id="section-\1">\1. \2</h2>', document)
    document = re.sub(r'<a href="([^"]+)">(.*?)</a>', source_link, document)
    document = document.replace("<table>", '<div class="table-wrap" tabindex="0" role="region" aria-label="Saved three-seed results"><table>').replace("</table>", "</table></div>")
    labels = ("Data", "Architecture", "Targets", "Training", "Joint training", "Decoders", "Next steps")
    nav = "".join(f'<a href="#section-{i}">{i} · {label}</a>' for i, label in enumerate(labels, 1))
    style = (HERE / "review.css").read_text() + (HERE / "widgets.css").read_text()
    widgets = (HERE / "widgets.js").read_text()
    payload = json.dumps(payload_obj, ensure_ascii=False, separators=(",", ":"), allow_nan=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    losses = json.dumps(losses_obj, ensure_ascii=False, separators=(",", ":"), allow_nan=False).replace("<", "\\u003c")
    assert "</script" not in widgets.lower() and "url(" not in style.lower()
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data: blob:; connect-src 'none'; base-uri 'none'; form-action 'none'"><title>Research review · neural recordings to prospective-path decoding · 28 September 2026</title><style>{style}</style></head>
<body id="top"><a class="skip" href="#section-1">Skip to review</a><div class="topbar"><nav aria-label="Review sections">{nav}</nav><button class="download" id="download-html" type="button" disabled>Download HTML</button><span class="download-status" id="download-status" role="status" aria-live="polite"></span></div>
<main><noscript><p class="no-js">The report, diagrams and saved training curves work without JavaScript. Enable JavaScript for the interactive latent viewer and download button, or save this HTML with your browser.</p></noscript>{document}<footer>Private laboratory discussion copy · completed exploratory evidence and explicitly proposed next steps. No new biological fitting. Every essential figure/data resource is embedded; external source links require repository access.</footer></main>
<script id="w-data" type="application/json">{payload}</script><script id="loss-data" type="application/json">{losses}</script><script>{widgets}</script><script>{DOWNLOAD_JS}</script></body></html>
'''
    check = PageCheck()
    check.feed(page)
    counts = Counter(check.ids)
    assert all(count == 1 for count in counts.values()), "Duplicate HTML/SVG IDs"
    assert all(fragment in counts for fragment in check.fragments), "Broken internal anchor"
    assert check.headings == 7 and check.canvases == 2 and check.scripts == 4
    assert all(f"section-{i}" in counts for i in range(1, 8))
    assert all(f"s{i}" in counts for i in range(1, 10))
    return page


def main() -> None:
    if not __debug__ or sys.argv[1:] not in ([], ["--check"]):
        raise SystemExit("Usage: python render.py [--check], without -O")
    try:
        result = render()
        if sys.argv[1:]:
            assert TARGET.read_text() == result, "Stale HTML: run render.py"
            print("PASS: saved numbers, rule arithmetic, cited paths, seven sections, anchors, offline resources, deterministic HTML")
        else:
            TARGET.write_text(result)
            print(f"Wrote {TARGET}")
    except (OSError, ValueError, KeyError, TypeError, AssertionError) as error:
        raise SystemExit(f"Review build/check failed: {error}") from error


if __name__ == "__main__":
    main()
