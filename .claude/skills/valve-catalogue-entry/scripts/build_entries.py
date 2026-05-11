#!/usr/bin/env python3
"""Batch generator for catalogue entries.

Renders one HTML entry per item in ENTRIES_DATA, using the skill's
entry-template CSS for visual consistency plus a category sidebar that
links every entry to every other. Append new entries to the list and
re-run to add more to the catalogue.
"""
from __future__ import annotations
import base64
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ASSETS = SCRIPT_DIR.parent / "assets"
DATA = SCRIPT_DIR.parent / "data"
ENTRIES_JSON = DATA / "entries.json"
REPO = SCRIPT_DIR.parents[3]
ENTRIES = REPO / "entries"
# Per-entry box-photo crops are tracked in the repo so the build script
# works on a fresh checkout (CI, a friend's clone, etc.). outputs/ is
# left as a scratch dir for the interactive workflow.
CROPS = REPO / "src-images" / "crops"
OUTPUTS = REPO / "outputs"


def load_entries() -> list[dict]:
    """Load the source-of-truth entries data from JSON."""
    return json.loads(ENTRIES_JSON.read_text())["entries"]


def save_entries(entries: list[dict]) -> None:
    """Persist entries back to JSON (used by process_submission.py)."""
    DATA.mkdir(parents=True, exist_ok=True)
    ENTRIES_JSON.write_text(
        json.dumps({"entries": entries}, indent=2, ensure_ascii=False) + "\n"
    )

# Category order is the order they appear in the sidebar and on the index.
CATEGORIES = [
    "Rectifiers",
    "RF / IF pentodes",
    "Frequency converters",
    "Output valves",
    "Other / TBD",
]


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def conf_pill(label: str, level: str) -> str:
    return f'<span class="conf {level}"><span class="dot"></span>{label}</span>'


def svg_for(env_key: str, code: str) -> str:
    fname = {
        "st-ux4": "st-ux4.svg",
        "octal": "octal.svg",
        "miniature-7pin": "miniature-7pin.svg",
        "miniature-9pin-noval": "miniature-9pin-noval.svg",
        # 6-pin small base — reuse st-ux4 with the right label; the visual
        # difference is in the pin count which is suggestive rather than
        # exact across the whole set anyway.
        "st-6pin": "st-ux4.svg",
    }[env_key]
    svg = (ASSETS / "svg-envelopes" / fname).read_text()
    return svg.replace("{{CODE}}", code)


def pills(items: list[str], cls: str) -> str:
    return "".join(f'<span class="pill {cls}">{x}</span>' for x in items)


def equivs_block(direct: list[str], subs: list[str]) -> str:
    out = []
    if direct:
        out.append('<p style="margin-bottom:8px;"><strong>Direct equivalents</strong> (same electricals &amp; base):</p>')
        out.append(f'<div class="pillrow" style="margin-bottom:12px;">{pills(direct, "same")}</div>')
    if subs:
        out.append('<p style="margin-bottom:8px;"><strong>Electrically same, different base</strong> (needs adapter / rewire):</p>')
        out.append(f'<div class="pillrow">{pills(subs, "alt")}</div>')
    if not out:
        out.append("<p>No widely-listed equivalents.</p>")
    return "\n        ".join(out)


def sources_block(items: list[tuple[str, str]]) -> str:
    return " ·\n    ".join(f'<a href="{url}">{label}</a>' for label, url in items)


# Extra CSS appended to the base template — sidebar layout and back-link.
EXTRA_CSS = """
.page {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 28px;
  max-width: 1200px;
  margin: 0 auto;
  align-items: start;
}
.sidebar {
  position: sticky; top: 24px;
  font-size: 13px; line-height: 1.4;
}
.sidebar .nav-home {
  display: inline-block; padding: 4px 0;
  font-size: 12px; letter-spacing: 0.04em;
  color: var(--muted); text-decoration: none;
  margin-bottom: 14px;
}
.sidebar .nav-home:hover { color: var(--accent); }
.sidebar .group { margin-bottom: 16px; }
.sidebar .group h3 {
  font-size: 10px; letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--muted); margin: 0 0 6px; font-weight: 700;
}
.sidebar ul { list-style: none; padding: 0; margin: 0; }
.sidebar a.entry-link {
  display: flex; gap: 8px; align-items: baseline;
  padding: 4px 10px; border-radius: 4px;
  text-decoration: none; color: var(--ink);
  font-size: 13px;
}
.sidebar a.entry-link:hover { background: #f1efe8; }
.sidebar a.entry-link.current {
  background: var(--accent-soft); color: var(--accent);
}
.sidebar a.entry-link .code {
  font-weight: 700; color: var(--accent); min-width: 52px;
  font-variant-numeric: tabular-nums;
}
.sidebar a.entry-link .brand {
  color: var(--muted); font-size: 11px;
}
.sidebar a.entry-link.current .brand { color: var(--accent); opacity: 0.85; }

main { min-width: 0; }
main .back-link {
  display: inline-block; margin-bottom: 8px;
  font-size: 12px; color: var(--muted); text-decoration: none;
}
main .back-link:hover { color: var(--accent); }

@media (max-width: 960px) {
  body { padding: 24px 16px 48px; }
  .page { grid-template-columns: 1fr; gap: 16px; }
  .sidebar { position: static; }
}
"""


# Shared CSS (from the canonical template — it has the .conf.high/.medium/.low
# level styling that entry 001 didn't have in its first iteration).
BASE_CSS = (ASSETS / "entry-template.html").read_text().split("<style>", 1)[1].split("</style>", 1)[0]
CSS = BASE_CSS + EXTRA_CSS


def render_sidebar(current_id: str | None, entries: list[dict]) -> str:
    """Build the grouped sidebar. If current_id is None, no item gets the
    `.current` highlight (used on the index page). Paths are written
    relative to entries/, then post-fixed for the index page by render_index().
    """
    parts = ['<a href="../index.html" class="nav-home">← Catalogue index</a>']
    by_cat: dict[str, list[dict]] = {c: [] for c in CATEGORIES}
    for e in entries:
        by_cat.setdefault(e["category"], []).append(e)
    for cat in CATEGORIES:
        items = by_cat.get(cat, [])
        if not items:
            continue
        parts.append(f'<div class="group"><h3>{cat}</h3><ul>')
        for e in sorted(items, key=lambda x: x["id"]):
            cls = "entry-link current" if e["id"] == current_id else "entry-link"
            parts.append(
                f'<li><a class="{cls}" href="{e["filename"]}">'
                f'<span class="code">{e["code"]}</span>'
                f'<span class="brand">{e["brand"]}</span>'
                f'</a></li>'
            )
        parts.append("</ul></div>")
    return "\n".join(parts)


def render(e: dict, all_entries: list[dict]) -> str:
    box_b64 = b64(CROPS / e["crop"])
    svg = svg_for(e["svg_key"], e["code"])
    heater_drop_row = (
        f'<dt>Heater drop</dt><dd>{e["heater_drop"]}</dd>' if e.get("heater_drop") else ""
    )
    mounting_row = (
        f'<dt>Mounting</dt><dd>{e["mounting"]}</dd>' if e.get("mounting") else ""
    )
    mil_row = (
        f'<dt>Mil. designation</dt><dd>{e["mil"]}</dd>' if e.get("mil") else ""
    )
    sidebar = render_sidebar(e["id"], all_entries)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Valve Catalogue — {e['brand']} {e['code']}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{CSS}</style>
</head>
<body>

<div class="page">

<aside class="sidebar">
{sidebar}
</aside>

<main>
<a href="../index.html" class="back-link">← All entries</a>

<div class="sheet">

  <header>
    <span class="tag">{e['function_tag']}</span>
    <div>
      <div class="eyebrow">Valve Catalogue · Entry</div>
      <h1>{e['brand']} <span class="code">{e['code']}</span></h1>
    </div>
    <span class="id">Entry #{e['id']} · Source: {e['source']}</span>
  </header>

  <p class="lede">
    {e['lede']}
  </p>

  <div class="imgs">
    <figure>
      <img src="data:image/jpeg;base64,{box_b64}" alt="Photograph of the {e['brand']} {e['code']} valve box, cropped from the catalogue source image.">
      <figcaption>Source photo · cropped from {e['source']}</figcaption>
    </figure>
    <figure>
      {svg}
      <figcaption>Reference · {e['envelope']} envelope, {e['base']} base</figcaption>
    </figure>
  </div>

  <div class="grid">
    <section class="col">
      <h2>Identification</h2>
      <dl>
        <dt>Code</dt><dd><strong>{e['code']}</strong></dd>
        <dt>Brand on box</dt><dd>{e['brand']}</dd>
        <dt>Country of origin</dt><dd>{e['country']}</dd>
        <dt>First introduced</dt><dd>{e['first_introduced']}</dd>
        <dt>Era</dt><dd>{e['era']}</dd>
        <dt>Confidence</dt><dd>{conf_pill(e['confidence_label'], e['confidence_class'])}</dd>
        {f'<dt>Count in photo</dt><dd>{e["count"]}</dd>' if e.get('count') else ''}
      </dl>
    </section>

    <section class="col">
      <h2>Type &amp; construction</h2>
      <dl>
        <dt>Function</dt><dd><strong>{e['function']}</strong></dd>
        <dt>Envelope</dt><dd>{e['envelope_detail']}</dd>
        <dt>Base</dt><dd>{e['base_detail']}</dd>
        <dt>Heating</dt><dd>{e['heating']}</dd>
        {heater_drop_row}
      </dl>
    </section>

    <section class="col">
      <h2>Key ratings</h2>
      <dl>
        <dt>{e['rating_1_label']}</dt><dd>{e['rating_1_value']}</dd>
        <dt>{e['rating_2_label']}</dt><dd>{e['rating_2_value']}</dd>
        <dt>Application</dt><dd>{e['application_short']}</dd>
        {mounting_row}
        {mil_row}
      </dl>
    </section>

    <section class="col">
      <h2>Typical applications</h2>
      <div class="prose">
        <p>{e['applications_prose']}</p>
      </div>
    </section>

    <section class="col">
      <h2>Equivalents &amp; substitutes</h2>
      <div class="prose">
        {equivs_block(e['direct_equivs'], e['substitutes'])}
      </div>
    </section>

    <section class="col">
      <h2>Approximate market value</h2>
      <div class="value-row">
        <div class="big">{e['value_range']}</div>
        <div class="note">{e['value_note']}</div>
      </div>
      <div class="prose" style="margin-top:10px;">
        <p>{e['value_prose']}</p>
      </div>
    </section>
  </div>

  <footer>
    <strong>Sources:</strong>
    {sources_block(e['sources'])}
    <br><br>
    <em>Catalogue entry · generated from {e['source']}.</em>
  </footer>

</div>

</main>

</div>

</body>
</html>
"""


# ENTRIES_DATA is loaded from .claude/skills/valve-catalogue-entry/data/entries.json
# at runtime. See load_entries() / save_entries() above for the read/write API.
ENTRIES_DATA = load_entries()


def main() -> None:
    for e in ENTRIES_DATA:
        html = render(e, ENTRIES_DATA)
        (ENTRIES / e["filename"]).write_text(html)
        print(f"wrote entries/{e['filename']}  ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
