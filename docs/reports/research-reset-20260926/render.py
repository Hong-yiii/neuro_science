"""Render/check this trusted local review; no research imports, data or model fits."""

import html
import re
import sys
from pathlib import Path

from markdown_it import MarkdownIt

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "README.md"
TARGET = HERE / "review.html"
STYLE = """
:root{color-scheme:light;--ink:#193832;--muted:#536760;--accent:#096653}
*{box-sizing:border-box}body{margin:0;background:#f4f2eb;color:var(--ink);font:17px/1.7 system-ui,sans-serif}
main{max-width:1120px;margin:auto;padding:48px 28px 90px}h1{font-size:clamp(2rem,4vw,3.5rem);line-height:1.12;max-width:900px}
h2{scroll-margin-top:160px;margin-top:3rem;padding-top:1rem;border-top:2px solid #ccd5ca;line-height:1.3}h3{margin-top:2rem;line-height:1.35}
a{color:var(--accent);text-underline-offset:3px}a:focus-visible{outline:3px solid #b86e1b;outline-offset:4px}
nav{position:sticky;top:0;z-index:1;background:#193832;padding:12px 24px;display:flex;gap:24px;flex-wrap:wrap}
nav a{color:white;font-size:.9rem}blockquote{margin:24px 0;padding:18px 24px;background:#e0ece3;border-left:5px solid #096653}
.table-wrap{overflow-x:auto;margin:24px 0;background:white;border:1px solid #cdd6ce}table{border-collapse:collapse;width:100%;font-size:.91rem}
th,td{padding:13px 16px;text-align:left;vertical-align:top;border-bottom:1px solid #dce2da}th{background:#e6ece3}
code{font-size:.86em;overflow-wrap:anywhere}pre{overflow:auto;background:#e9ebe4;padding:16px}li{margin:.45em 0}
.local-source{color:var(--muted);font-size:.82em}footer{margin-top:40px;color:var(--muted);font-size:.9rem}
@media(max-width:600px){main{padding:22px 16px}nav{gap:12px;padding:10px 16px}table{min-width:660px}}
@media print{nav{display:none}body{background:white}main{padding:0}h2{break-after:avoid}.table-wrap{overflow:visible}table{min-width:0}}
"""


def render() -> str:
    """Use the existing MarkdownIt dependency; local references stay visible offline."""
    document = (
        MarkdownIt("commonmark", {"html": True})
        .enable("table")
        .render(SOURCE.read_text())
    )
    sections = []

    def heading(match: re.Match[str]) -> str:
        number, title = match.groups()
        sections.append((number, title.split(" — ")[0]))
        return f'<h2 id="section-{number}">{number}. {title}</h2>'

    document = re.sub(r"<h2>(\d+)\. (.*?)</h2>", heading, document)

    def local_link(match: re.Match[str]) -> str:
        href, label = match.groups()
        if href.startswith(("https://", "http://", "#")):
            return match.group(0)
        if href == "review.html":
            return '<a href="#top">Portable review · currently open</a>'
        resolved = (HERE / href).resolve()
        assert resolved.is_file(), f"Missing local reference: {href}"
        relative = resolved.relative_to(HERE.parents[2])
        # ponytail: show local paths offline instead of inventing public URLs for uncommitted reports.
        return f'{label} <span class="local-source">[local: <code>{html.escape(str(relative))}</code>]</span>'

    document = re.sub(r'<a href="([^"]+)">(.*?)</a>', local_link, document)
    document = document.replace("<table>", '<div class="table-wrap"><table>').replace(
        "</table>", "</table></div>"
    )
    assert len(sections) == 7, "Review trajectory lost a section"
    short_titles = (
        "Route",
        "This week",
        "Open questions",
        "Options",
        "Cleanup",
        "Decide",
        "Sources",
    )
    navigation = "".join(
        f'<a href="#section-{n}">{n} · {title}</a>'
        for (n, _), title in zip(sections, short_titles, strict=True)
    )
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light"><title>Neuroscience · research reset · 26 September 2026</title>
<style>{STYLE}</style></head><body id="top"><nav aria-label="Review sections">{navigation}</nav>
<main>{document}<footer>Offline decision review. No scripts, external resources or running server. Print or save this page to retain a local copy.</footer></main></body></html>"""
    assert "primary criterion failed" in page and "26,266 new fits this week" in page
    assert not re.search(r"<(script|iframe|img|link)\b|\bsrc=|url\(", page, re.I), (
        "Unexpected external or active content"
    )
    assert all(
        f'id="{anchor}"' in page for anchor in re.findall(r'href="#([^"]+)"', page)
    ), "Broken section anchor"
    return page


if __name__ == "__main__":
    if not __debug__:
        raise SystemExit("Run without -O: this renderer's checks require assertions")
    if sys.argv[1:] not in ([], ["--check"]):
        raise SystemExit("Usage: render.py [--check]")
    result = render()
    if sys.argv[1:]:
        assert TARGET.read_text() == result, "HTML is stale; rerun render.py"
        print(
            "PASS: rendered bytes, seven sections, anchors, local references, no active/external resources"
        )
    else:
        TARGET.write_text(result)
        print(f"Wrote {TARGET}")
