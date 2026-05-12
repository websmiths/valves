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
SOURCES_JSON = DATA / "sources.json"
REPO = SCRIPT_DIR.parents[3]
ENTRIES = REPO / "entries"
SOURCES = REPO / "sources"           # per-photo HTML pages live here
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


def load_sources() -> list[dict]:
    """Load the source-photos metadata (provenance notes etc)."""
    if not SOURCES_JSON.exists():
        return []
    return json.loads(SOURCES_JSON.read_text())["sources"]


def save_sources(sources: list[dict]) -> None:
    """Persist source-photos metadata."""
    DATA.mkdir(parents=True, exist_ok=True)
    SOURCES_JSON.write_text(
        json.dumps({"sources": sources}, indent=2, ensure_ascii=False) + "\n"
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

    # Inventory rows in the Identification block:
    #   - "Inventory": total count — always shown, default 1
    #   - "Also in": secondary source photos beyond the primary one
    raw_count = e.get("count")
    try:
        count_n = int(str(raw_count).strip()) if raw_count is not None else None
    except (TypeError, ValueError):
        # Free-form legacy count strings (e.g. "≈ 5 boxes present") — show as-is
        count_n = None
    if count_n is not None:
        plural = "" if count_n == 1 else "es"
        count_row = f'<dt>Inventory</dt><dd><strong>{count_n}</strong> box{plural} in collection</dd>'
    elif raw_count:
        count_row = f'<dt>Inventory</dt><dd>{raw_count}</dd>'
    else:
        count_row = '<dt>Inventory</dt><dd><strong>1</strong> box in collection</dd>'

    extra_sources_row = ""
    extras = e.get("additional_sources") or []
    if extras:
        links = ", ".join(f"<code>{s}</code>" for s in extras)
        extra_sources_row = f'<dt>Also in</dt><dd>{links}</dd>'
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
    <span class="id">Source: <a href="../sources/{e['source'].rsplit('.', 1)[0]}.html">{e['source']}</a></span>
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
        {count_row}
        {extra_sources_row}
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


# Additional CSS appended to the entry-template CSS for source pages.
# Reuses the existing .page / .sidebar / .sheet shell.
SOURCE_PAGE_EXTRA_CSS = """
.source-figure {
  margin: 0; padding: 28px 32px; text-align: center;
  border-bottom: 1px solid var(--line);
  display: flex; flex-direction: column; align-items: center; gap: 12px;
}
.source-figure img {
  max-width: 100%; max-height: 540px; width: auto;
  border-radius: 4px;
  box-shadow: 0 1px 0 rgba(0,0,0,0.02), 0 4px 14px rgba(40,30,10,0.06);
}
.source-figure figcaption {
  font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--muted);
}
.source-meta {
  padding: 16px 32px 24px; border-bottom: 1px solid var(--line);
}
.source-meta dl {
  display: grid; grid-template-columns: 140px 1fr;
  row-gap: 6px; column-gap: 12px; margin: 0;
  font-size: 14px; line-height: 1.45;
}
.source-meta dt { color: var(--muted); font-weight: 500; }
.source-meta dd { margin: 0; color: var(--ink); }
.source-entries { padding: 18px 32px 24px; }
.source-entries h2 {
  margin: 0 0 12px; font-size: 11px; font-weight: 700;
  letter-spacing: 0.16em; text-transform: uppercase; color: var(--muted);
}
.source-entries ul { list-style: none; padding: 0; margin: 0; }
.source-entries li { padding: 8px 0; border-bottom: 1px solid var(--line); }
.source-entries li:last-child { border-bottom: 0; }
.source-entries a {
  display: flex; gap: 12px; align-items: baseline;
  text-decoration: none; color: var(--ink);
}
.source-entries a:hover .code { text-decoration: underline; }
.source-entries .code {
  font-weight: 700; color: var(--accent); min-width: 72px;
}
.source-entries .brand { color: var(--muted); font-size: 13px; min-width: 130px; }
.source-entries .conf { font-size: 11px; }
"""


def render_source_page(source: dict, all_entries: list[dict]) -> str:
    """Render one source-photo page (sources/<basename>.html)."""
    filename = source["filename"]
    stem = filename.rsplit(".", 1)[0]
    note = (source.get("note") or "").strip()

    # Sidebar links use a different relative root from the entry pages
    # because source pages live at /sources/, not /entries/. Adjust the
    # entry-link hrefs at render time.
    sidebar = render_sidebar(current_id=None, entries=all_entries)
    sidebar = sidebar.replace('href="../index.html"', 'href="../index.html"')
    # The sidebar's entry-links are emitted as e.g. href="001-rca-5z3.html"
    # — relative to /entries/. From /sources/ that needs to be ../entries/...
    import re as _re
    sidebar = _re.sub(
        r'href="((?!\.\.|http|/)[^"]+\.html)"',
        r'href="../entries/\1"',
        sidebar,
    )

    # Entries derived from this photo (primary source OR additional source)
    derived = [
        e for e in all_entries
        if e.get("source") == filename
        or filename in (e.get("additional_sources") or [])
    ]
    derived.sort(key=lambda e: e["id"])
    if derived:
        entries_html_parts = ["<ul>"]
        for e in derived:
            entries_html_parts.append(
                f'<li><a href="../entries/{e["filename"]}">'
                f'<span class="code">{e["code"]}</span>'
                f'<span class="brand">{e["brand"]}</span>'
                f'<span class="conf">{e["confidence_label"]}</span>'
                f'</a></li>'
            )
        entries_html_parts.append("</ul>")
        entries_html = "\n".join(entries_html_parts)
    else:
        entries_html = '<p style="color:var(--muted);">No entries derived from this photo yet.</p>'

    submitted_at = source.get("submitted_at")
    submitted_at_row = (
        f'<dt>Submitted</dt><dd>{submitted_at}</dd>'
        if submitted_at else ""
    )
    note_block = (
        f'<p class="lede">{note}</p>'
        if note
        else '<p class="lede" style="font-style:italic;">No provenance note recorded for this photo.</p>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Valve Catalogue — Source · {filename}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{CSS}{SOURCE_PAGE_EXTRA_CSS}</style>
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
    <span class="tag">Source photo</span>
    <div>
      <div class="eyebrow">Valve Catalogue · Source</div>
      <h1>{filename}</h1>
    </div>
    <span class="id">{len(derived)} {'entry' if len(derived) == 1 else 'entries'} derived</span>
  </header>

  {note_block}

  <figure class="source-figure">
    <img src="../src-images/{filename}" alt="Source photograph: {filename}">
    <figcaption>Source photograph · {filename}</figcaption>
  </figure>

  <section class="source-meta">
    <dl>
      <dt>Filename</dt><dd><code>src-images/{filename}</code></dd>
      <dt>Entries derived</dt><dd>{len(derived)}</dd>
      {submitted_at_row}
    </dl>
  </section>

  <section class="source-entries">
    <h2>Entries from this photo</h2>
    {entries_html}
  </section>

</div>

</main>

</div>

</body>
</html>
"""


def main() -> None:
    # Entry pages
    for e in ENTRIES_DATA:
        html = render(e, ENTRIES_DATA)
        (ENTRIES / e["filename"]).write_text(html)
        print(f"wrote entries/{e['filename']}  ({len(html):,} bytes)")

    # Source-photo pages — one per unique source referenced by entries.
    SOURCES.mkdir(parents=True, exist_ok=True)
    sources_meta = {s["filename"]: s for s in load_sources()}
    referenced_sources: list[str] = []
    seen: set[str] = set()
    for e in ENTRIES_DATA:
        for s in [e.get("source")] + (e.get("additional_sources") or []):
            if s and s not in seen:
                seen.add(s)
                referenced_sources.append(s)
    for s_filename in referenced_sources:
        source = sources_meta.get(s_filename, {"filename": s_filename, "note": "", "submitted_at": None})
        html = render_source_page(source, ENTRIES_DATA)
        stem = s_filename.rsplit(".", 1)[0]
        (SOURCES / f"{stem}.html").write_text(html)
        print(f"wrote sources/{stem}.html  ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
