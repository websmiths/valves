#!/usr/bin/env python3
"""Batch generator for catalogue entries.

Renders one HTML entry per item in ENTRIES_DATA, using the skill's
entry-template CSS for visual consistency plus a category sidebar that
links every entry to every other. Append new entries to the list and
re-run to add more to the catalogue.
"""
from __future__ import annotations
import base64
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ASSETS = SCRIPT_DIR.parent / "assets"
REPO = SCRIPT_DIR.parents[3]
ENTRIES = REPO / "entries"
OUTPUTS = REPO / "outputs"

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
    box_b64 = b64(OUTPUTS / e["crop"])
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


ENTRIES_DATA = [
    {  # 001 — RCA 5Z3 (was hand-built originally; now folded into the generator)
        "id": "001", "filename": "001-rca-5z3.html",
        "brand": "RCA", "code": "5Z3",
        "category": "Rectifiers",
        "function_tag": "Rectifier",
        "source": "boxes-1.jpeg", "crop": "entry-001-crop.jpeg",
        "svg_key": "st-ux4",
        "lede": (
            "Full-wave high-vacuum rectifier with a 4-pin UX base. Used in "
            "1930s–40s valve receivers and amplifiers where a high-current "
            "B+ supply was needed. Electrically identical to the more "
            "familiar octal-based <strong>5U4G</strong>, just on the older "
            "4-pin socket."
        ),
        "country": "USA (also made by Marconi CA, Brimar UK, others under licence)",
        "first_introduced": "1933",
        "era": "1933 – mid 1950s",
        "confidence_label": "High · code legible",
        "confidence_class": "high",
        "function": "Full-wave vacuum rectifier",
        "envelope": "ST-shape",
        "envelope_detail": "ST-shape glass, ~52 × 130 mm",
        "base": "UX4",
        "base_detail": "UX4 (4 pins, 2 thick / 2 thin)",
        "heating": "Directly heated filament, 5.0 V AC, 3.0 A",
        "heater_drop": "~50 V",
        "rating_1_label": "Max plate voltage",
        "rating_1_value": "~450 V RMS per plate",
        "rating_2_label": "Max DC output",
        "rating_2_value": "~225 mA",
        "application_short": "HT (B+) supply in receivers &amp; amps",
        "mounting": "Vertical, base down preferred",
        "mil": "VT-145 (JAN-CRC-5Z3)",
        "applications_prose": (
            "HT power supply rectifier in valve radios (broadcast and "
            "communications receivers, 1933–50s), Hammond-style organs, "
            "early hi-fi and guitar amplifiers, and laboratory power "
            "supplies needing a high-current 5V-heated rectifier on the "
            "older 4-pin socket."
        ),
        "direct_equivs": ["KX5Z3", "5Z3G", "NU-5Z3", "VT-145"],
        "substitutes": ["5U4G (octal)", "5X4G (octal)", "5T4"],
        "value_range": "A$25 – A$60",
        "value_note": "NOS, boxed, single tube",
        "value_prose": (
            "Used / tested pulls trade lower (A$10–25). RCA black-plate and "
            "JAN-CRC military variants command a premium. Less sought-after "
            "than the 5U4G because most modern amps use the octal base."
        ),
        "sources": [
            ("Radiomuseum.org — 5Z3", "https://www.radiomuseum.org/tubes/tube_5z3.html"),
            ("Frank's Tube Data — 5Z3 datasheet (PDF)", "https://frank.pocnet.net/sheets/021/5/5Z3.pdf"),
            ("Amplified Parts — 5Z3", "https://www.amplifiedparts.com/products/vacuum-tube-5z3-rectifier-full-wave"),
            ("Smithsonian NMAH — RCA 5Z3", "https://americanhistory.si.edu/collections/object/nmah_702068"),
            ("VinylSavor — Tube of the Month: 5Z3", "http://vinylsavor.blogspot.com/2021/10/tube-of-month-5z3.html"),
        ],
    },
    {  # 002 — Radiotron 80
        "id": "002", "filename": "002-radiotron-80.html",
        "brand": "Radiotron", "code": "80",
        "category": "Rectifiers",
        "function_tag": "Rectifier",
        "source": "boxes-1.jpeg", "crop": "entry-002-crop.jpeg",
        "svg_key": "st-ux4",
        "lede": (
            "Pre-octal full-wave high-vacuum rectifier — one of the original "
            "Western Electric / RCA tube families, dating to 1927. 5-volt, "
            "2-amp directly-heated filament on the 4-pin UX socket. The "
            "octal-era replacement is the <strong>5Y3G</strong>, with which "
            "the 80 is electrically identical."
        ),
        "country": "Australia (AWV / RCA-Radiotron), originally USA (RCA)",
        "first_introduced": "1927 (RCA UX-280)",
        "era": "1927 – late 1950s",
        "confidence_label": "High · printed factory label",
        "confidence_class": "high",
        "count": "4 boxes present",
        "function": "Full-wave vacuum rectifier",
        "envelope": "ST-shape",
        "envelope_detail": "ST-shape glass, ~52 × 130 mm",
        "base": "UX4",
        "base_detail": "UX4 (4 pins, 2 thick / 2 thin)",
        "heating": "Directly heated filament, 5.0 V AC, 2.0 A",
        "heater_drop": "~50 V",
        "rating_1_label": "Max plate voltage",
        "rating_1_value": "~350 V RMS per plate",
        "rating_2_label": "Max DC output",
        "rating_2_value": "~125 mA",
        "application_short": "HT (B+) supply in domestic receivers &amp; small amps",
        "mounting": "Vertical, base down",
        "mil": "VT-71 (military designation)",
        "applications_prose": (
            "The 80 was the standard B+ rectifier in AC-mains broadcast "
            "receivers from the late 1920s through the 1940s — most Radiola, "
            "Astor and AWA console sets of the era used one. Also common in "
            "Hammond-style organs and laboratory power supplies that needed "
            "a modest-current rectifier on the older 4-pin socket."
        ),
        "direct_equivs": ["UX-280", "5Y3 (early)", "KX-80"],
        "substitutes": ["5Y3G (octal)", "5Y3GT (octal)", "5T4"],
        "value_range": "A$20 – A$45",
        "value_note": "NOS, boxed, single tube",
        "value_prose": (
            "Common Australian-made AWV / Radiotron stock is at the lower "
            "end; early RCA mesh-plate or balloon-shape (UX-280) variants "
            "trade higher. Used / tested-good pulls A$8–20."
        ),
        "sources": [
            ("Radiomuseum.org — 80", "https://www.radiomuseum.org/tubes/tube_80.html"),
            ("Frank's Tube Data — 80 datasheet", "https://frank.pocnet.net/sheets/049/8/80.pdf"),
            ("The Valve Store (AU)", "https://thevalvestore.com.au/"),
            ("Aussie Audio Mart — vintage valve listings", "https://www.aussieaudiomart.com/"),
        ],
    },
    {  # 003 — Radiotron 78
        "id": "003", "filename": "003-radiotron-78.html",
        "brand": "Radiotron", "code": "78",
        "category": "RF / IF pentodes",
        "function_tag": "RF / IF pentode",
        "source": "boxes-1.jpeg", "crop": "entry-003-crop.jpeg",
        "svg_key": "st-6pin",
        "lede": (
            "Variable-mu (remote-cutoff) RF / IF pentode introduced by RCA "
            "in 1932. Effectively identical electricals to the better-known "
            "<strong>6D6</strong> — same heater, same 6-pin small base, same "
            "characteristics — and the two are routinely listed as direct "
            "equivalents."
        ),
        "country": "Australia (AWV / RCA-Radiotron)",
        "first_introduced": "1932",
        "era": "1932 – mid 1950s",
        "confidence_label": "High · printed factory label",
        "confidence_class": "high",
        "function": "Remote-cutoff RF / IF pentode (variable-mu)",
        "envelope": "ST-shape",
        "envelope_detail": "ST-shape glass, top-cap control grid",
        "base": "6-pin small (\"small 6\")",
        "base_detail": "6-pin small with top-cap control grid",
        "heating": "Indirectly heated, 6.3 V, 0.3 A",
        "rating_1_label": "Max plate voltage",
        "rating_1_value": "250 V",
        "rating_2_label": "Mutual conductance",
        "rating_2_value": "~1.45 mA/V",
        "application_short": "RF and IF amplification with AGC (variable-mu action)",
        "applications_prose": (
            "Standard variable-mu pentode in mid-1930s superhet broadcast "
            "and short-wave receivers — the RF and IF stages of almost "
            "every domestic radio from about 1933 to 1936, before the "
            "octal-base 6U7G and miniature 6BA6 took over. Pairs naturally "
            "with the sharp-cutoff 6C6 as detector / first-AF."
        ),
        "direct_equivs": ["6D6", "Mullard VMP4G"],
        "substitutes": ["6U7G (octal)", "6K7 (octal, metal)", "6BA6 (B7G miniature)"],
        "value_range": "A$15 – A$30",
        "value_note": "NOS, boxed, single tube",
        "value_prose": (
            "Plentiful in vintage-radio circles, so prices stay modest. "
            "Used / tested-good pulls A$5–12. Premium for sealed RCA "
            "black-plate or Marconi-Osram examples."
        ),
        "sources": [
            ("Radiomuseum.org — 78", "https://www.radiomuseum.org/tubes/tube_78.html"),
            ("Frank's Tube Data — 78 datasheet", "https://frank.pocnet.net/sheets/049/7/78.pdf"),
            ("The Valve Store (AU)", "https://thevalvestore.com.au/"),
        ],
    },
    {  # 004 — Radiotron 6D6
        "id": "004", "filename": "004-radiotron-6d6.html",
        "brand": "Super Radiotron", "code": "6D6",
        "category": "RF / IF pentodes",
        "function_tag": "RF / IF pentode",
        "source": "boxes-1.jpeg", "crop": "entry-004-crop.jpeg",
        "svg_key": "st-6pin",
        "lede": (
            "Variable-mu (remote-cutoff) RF / IF pentode — the direct "
            "successor to the type 78, with which it shares heater, base, "
            "pinout and characteristics. Approximately five boxes of this "
            "type are present in the source frame, all with handwritten "
            "labels on Australian AWV \"Super Radiotron\" cartons."
        ),
        "country": "Australia (AWV / RCA-Radiotron, Sydney)",
        "first_introduced": "1933",
        "era": "1933 – late 1950s",
        "confidence_label": "Medium · code is handwritten on the carton sticker",
        "confidence_class": "medium",
        "count": "≈ 5 boxes present",
        "function": "Remote-cutoff RF / IF pentode (variable-mu)",
        "envelope": "ST-shape",
        "envelope_detail": "ST-shape glass, top-cap control grid",
        "base": "6-pin small",
        "base_detail": "6-pin small with top-cap control grid",
        "heating": "Indirectly heated, 6.3 V, 0.3 A",
        "rating_1_label": "Max plate voltage",
        "rating_1_value": "250 V",
        "rating_2_label": "Mutual conductance",
        "rating_2_value": "~1.6 mA/V",
        "application_short": "RF / IF amplifier with AGC",
        "applications_prose": (
            "RF and IF stages of broadcast and short-wave superhet "
            "receivers from 1933 onward — the workhorse remote-cutoff "
            "pentode of the pre-octal era. Australian sets from AWA, "
            "Astor, Healing and HMV used it extensively. The variable-mu "
            "characteristic lets the stage gain be reduced cleanly by AGC "
            "bias."
        ),
        "direct_equivs": ["Type 78", "Mullard VMP4G", "Marconi-Osram MVS/Pen"],
        "substitutes": ["6U7G (octal)", "6K7 (octal)", "EF39 (8-pin)"],
        "value_range": "A$15 – A$25",
        "value_note": "NOS, boxed, single tube",
        "value_prose": (
            "Common and cheap on the second-hand market — supply outstrips "
            "demand because most surviving radios already have one. Used "
            "pulls A$5–10. Boxed Australian-made Radiotron examples in "
            "original cartons (as here) carry a small collector premium."
        ),
        "sources": [
            ("Radiomuseum.org — 6D6", "https://www.radiomuseum.org/tubes/tube_6d6.html"),
            ("Frank's Tube Data — 6D6 datasheet", "https://frank.pocnet.net/sheets/049/6/6D6.pdf"),
            ("The Valve Store (AU)", "https://thevalvestore.com.au/"),
        ],
    },
    {  # 005 — Radiotron 6C6
        "id": "005", "filename": "005-radiotron-6c6.html",
        "brand": "Radiotron", "code": "6C6",
        "category": "RF / IF pentodes",
        "function_tag": "RF / detector pentode",
        "source": "boxes-1.jpeg", "crop": "entry-005-crop.jpeg",
        "svg_key": "st-6pin",
        "lede": (
            "Sharp-cutoff RF / detector pentode — the fixed-mu counterpart "
            "to the 6D6. Same 6-pin small base, same 6.3 V heater, same "
            "envelope; the difference is the control-grid characteristic, "
            "which suits first-detector and AF roles where AGC isn't "
            "applied."
        ),
        "country": "Australia (AWV / RCA-Radiotron)",
        "first_introduced": "1933",
        "era": "1933 – late 1950s",
        "confidence_label": "Medium · code is handwritten on the carton sticker",
        "confidence_class": "medium",
        "function": "Sharp-cutoff RF / detector pentode",
        "envelope": "ST-shape",
        "envelope_detail": "ST-shape glass, top-cap control grid",
        "base": "6-pin small",
        "base_detail": "6-pin small with top-cap control grid",
        "heating": "Indirectly heated, 6.3 V, 0.3 A",
        "rating_1_label": "Max plate voltage",
        "rating_1_value": "250 V",
        "rating_2_label": "Mutual conductance",
        "rating_2_value": "~1.2 mA/V",
        "application_short": "Detector, audio voltage amplifier, first-stage RF without AGC",
        "applications_prose": (
            "Where the 6D6 was the controlled-gain RF/IF tube, the 6C6 was "
            "the fixed-gain partner — used as the grid-leak or plate "
            "detector, the first audio amplifier stage, or as a low-noise "
            "RF stage in short-wave sets. Paired with a 6D6 in countless "
            "1930s Australian superhets. Octal-base successor: 6J7."
        ),
        "direct_equivs": ["Type 77", "Mullard SP4"],
        "substitutes": ["6J7 (octal)", "6SJ7 (octal)", "EF37A (8-pin)"],
        "value_range": "A$15 – A$25",
        "value_note": "NOS, boxed, single tube",
        "value_prose": (
            "Roughly the same market as the 6D6 — common, plentiful, "
            "modestly priced. Used pulls A$5–10. The 6C6 is slightly "
            "scarcer than the 6D6 since fewer were needed per set."
        ),
        "sources": [
            ("Radiomuseum.org — 6C6", "https://www.radiomuseum.org/tubes/tube_6c6.html"),
            ("Frank's Tube Data — 6C6 datasheet", "https://frank.pocnet.net/sheets/049/6/6C6.pdf"),
            ("The Valve Store (AU)", "https://thevalvestore.com.au/"),
        ],
    },
    {  # 006 — Radiotron 6X5GT
        "id": "006", "filename": "006-radiotron-6x5gt.html",
        "brand": "Radiotron", "code": "6X5GT",
        "category": "Rectifiers",
        "function_tag": "Rectifier",
        "source": "boxes-1.jpeg", "crop": "entry-006-crop.jpeg",
        "svg_key": "octal",
        "lede": (
            "Indirectly-heated full-wave rectifier on the octal base — the "
            "small-signal partner to the 5Y3GT for receiver-sized B+ "
            "supplies. Heater is 6.3 V so it can share a transformer "
            "winding with the signal valves, simplifying AC/DC and "
            "car-radio designs."
        ),
        "country": "Australia (AWV / RCA-Radiotron)",
        "first_introduced": "1937",
        "era": "1937 – late 1960s",
        "confidence_label": "High · printed factory label",
        "confidence_class": "high",
        "function": "Full-wave vacuum rectifier (indirectly heated)",
        "envelope": "GT-shape",
        "envelope_detail": "GT-shape glass, ~30 × 80 mm",
        "base": "Octal (8-pin)",
        "base_detail": "Octal (8-pin, key-locked centre spigot)",
        "heating": "Indirectly heated cathode, 6.3 V, 0.6 A",
        "rating_1_label": "Max plate voltage",
        "rating_1_value": "350 V RMS per plate",
        "rating_2_label": "Max DC output",
        "rating_2_value": "70 mA",
        "application_short": "B+ supply for receivers, small amps, car radios",
        "mounting": "Any orientation",
        "applications_prose": (
            "The 6X5GT was the rectifier of choice for valve car radios "
            "and small AC mains receivers from the late 1930s onward, "
            "because the 6.3 V heater meant one transformer winding (or "
            "vibrator inverter) could supply every valve in the set. Also "
            "common in test gear, small organs and intercom amplifiers."
        ),
        "direct_equivs": ["6X5", "6X5G", "VT-126"],
        "substitutes": ["5Y3GT (5V heater, ~125 mA)", "EZ80 (B9A)", "EZ81 (B9A)"],
        "value_range": "A$15 – A$30",
        "value_note": "NOS, boxed, single tube",
        "value_prose": (
            "Common and widely available. Premium for early black-glass "
            "GT envelopes or Marconi-Osram \"red label\" examples. The "
            "closely-related 6X4 (B7G miniature) is the post-war "
            "replacement in compact sets."
        ),
        "sources": [
            ("Radiomuseum.org — 6X5GT", "https://www.radiomuseum.org/tubes/tube_6x5gt.html"),
            ("Frank's Tube Data — 6X5GT datasheet", "https://frank.pocnet.net/sheets/030/6/6X5GT.pdf"),
            ("The Valve Store (AU)", "https://thevalvestore.com.au/"),
        ],
    },
    {  # 007 — GEC KT66
        "id": "007", "filename": "007-gec-kt66.html",
        "brand": "G.E.C.", "code": "KT66",
        "category": "Output valves",
        "function_tag": "Output beam tetrode",
        "source": "boxes-1.jpeg", "crop": "entry-007-crop.jpeg",
        "svg_key": "octal",
        "lede": (
            "The Marconi-Osram / GEC <strong>KT66</strong> is one of the "
            "most sought-after British audio output valves ever made — a "
            "kinkless beam tetrode that became the voice of early Marshall "
            "guitar amps, the Leak TL12 and the McIntosh MC75. Roughly "
            "interchangeable with the American 6L6 family, but with a "
            "distinctly British tonal signature and premium build quality."
        ),
        "country": "United Kingdom (Marconi-Osram Valve Co. / GEC, Hammersmith)",
        "first_introduced": "1937",
        "era": "1937 – late 1960s (original GEC production)",
        "confidence_label": "Medium · code handwritten in pencil on the GEC carton",
        "confidence_class": "medium",
        "function": "Kinkless (beam) power tetrode",
        "envelope": "ST / coke-bottle, large",
        "envelope_detail": "Large ST glass, ~52 × 120 mm",
        "base": "Octal",
        "base_detail": "International octal, key-locked centre spigot",
        "heating": "Indirectly heated cathode, 6.3 V, 1.27 A",
        "rating_1_label": "Max plate voltage",
        "rating_1_value": "500 V",
        "rating_2_label": "Max plate dissipation",
        "rating_2_value": "25 W",
        "application_short": "Class-A or AB push-pull audio output (~30 W per pair)",
        "mounting": "Any orientation; base-down preferred for amps",
        "mil": "CV1075 (British military)",
        "applications_prose": (
            "Originally designed by M-O Valve Co. as a higher-quality "
            "British answer to the RCA 6L6. Became famous as the output "
            "stage of the Leak Point One and TL/10 amplifiers, the "
            "McIntosh MC30 and MC75, and — most famously — early Marshall "
            "JTM45 guitar amplifiers before Marshall switched to the 5881 "
            "/ 6L6GC for cost reasons. Studio engineers still pay a "
            "premium for genuine GEC KT66s for Marshall reissues and "
            "bespoke hi-fi builds."
        ),
        "direct_equivs": ["CV1075 (mil.)", "Genalex KT66 (reissue)"],
        "substitutes": ["6L6G / 6L6GC", "5881", "7027A (with bias adjust)"],
        "value_range": "A$200 – A$400+",
        "value_note": "NOS, boxed, single tube · matched pairs higher",
        "value_prose": (
            "Genuine GEC / M-O Valve KT66s in original GEC cartons are "
            "the premium tier: A$300 / pair is common on Aussie Audio "
            "Mart and matched quads run A$500–700. Reissue Genalex (New "
            "Sensor) tubes sell for A$80–120 each new and don't trade on "
            "the vintage market. Authenticate by the GEC etch on the "
            "glass and the brown micanol base — fakes exist."
        ),
        "sources": [
            ("Radiomuseum.org — KT66", "https://www.radiomuseum.org/tubes/tube_kt66.html"),
            ("Frank's Tube Data — KT66 datasheet", "https://frank.pocnet.net/sheets/010/k/KT66.pdf"),
            ("Aussie Audio Mart — GEC KT66 NOS listings", "https://www.aussieaudiomart.com/details/649323642-very-rare-gec-kt66-nos-valve-collection/"),
            ("Watford Valves — KT66 reference", "https://www.watfordvalves.com/products.asp?search=kt66"),
        ],
    },
    {  # 008 — Radiotron 6B7S
        "id": "008", "filename": "008-radiotron-6b7s.html",
        "brand": "Radiotron", "code": "6B7S",
        "category": "RF / IF pentodes",
        "function_tag": "Duo-diode pentode",
        "source": "boxes-1.jpeg", "crop": "entry-008-crop.jpeg",
        "svg_key": "st-6pin",
        "lede": (
            "Australian-made duo-diode pentode — two diodes for AM "
            "detection / AGC plus a sharp-cutoff pentode in one envelope, "
            "all in a single 7-pin small base with a top-cap control grid. "
            "The \"S\" suffix on Australian Radiotron / AWV cartons "
            "indicates a \"Super\" / Sydney-made variant of the otherwise "
            "identical 6B7."
        ),
        "country": "Australia (AWV / RCA-Radiotron, Sydney)",
        "first_introduced": "1933 (RCA 6B7)",
        "era": "1933 – late 1940s",
        "confidence_label": "High · printed factory label",
        "confidence_class": "high",
        "count": "≈ 2 boxes present",
        "function": "Duplex-diode sharp-cutoff pentode",
        "envelope": "ST-shape",
        "envelope_detail": "ST-shape glass, top-cap control grid",
        "base": "7-pin small",
        "base_detail": "7-pin small with top-cap control grid",
        "heating": "Indirectly heated, 6.3 V, 0.3 A",
        "rating_1_label": "Max plate voltage",
        "rating_1_value": "250 V (pentode)",
        "rating_2_label": "Mutual conductance",
        "rating_2_value": "~1.1 mA/V",
        "application_short": "Combined detector / AVC / first-AF stage in 1930s superhets",
        "applications_prose": (
            "The 6B7 family did three jobs in one envelope — the two "
            "diode plates handled second-detection of the IF signal and "
            "produced AGC voltage, while the pentode acted as the first "
            "audio amplifier. Standard fit in Australian and US "
            "broadcast superhets from about 1933 until the octal "
            "6B8G / 6SQ7 took over. Equivalent to the German EBF2 in "
            "function (though pinout differs)."
        ),
        "direct_equivs": ["6B7", "6B7G (Australian)"],
        "substitutes": ["6B8G (octal)", "6SQ7 (octal, diode-triode)", "EBF2 (8-pin)"],
        "value_range": "A$15 – A$30",
        "value_note": "NOS, boxed, single tube",
        "value_prose": (
            "Less common than the 6D6 / 6C6 but not rare. Boxed AWV "
            "Australian-made examples (as here) carry a small premium "
            "with vintage-radio restorers. Used pulls A$5–12."
        ),
        "sources": [
            ("Radiomuseum.org — 6B7", "https://www.radiomuseum.org/tubes/tube_6b7.html"),
            ("Frank's Tube Data — 6B7 datasheet", "https://frank.pocnet.net/sheets/049/6/6B7.pdf"),
            ("The Valve Store (AU)", "https://thevalvestore.com.au/"),
        ],
    },
    {  # 009 — Super Radiotron 6J7
        "id": "009", "filename": "009-radiotron-6j7.html",
        "brand": "Super Radiotron", "code": "6J7",
        "category": "RF / IF pentodes",
        "function_tag": "RF / IF pentode",
        "source": "boxes-1.jpeg", "crop": "entry-009-crop.jpeg",
        "svg_key": "octal",
        "lede": (
            "Sharp-cutoff RF / IF / detector pentode on the octal base — "
            "the direct octal successor to the pre-octal 6C6. Top-cap "
            "control grid, 6.3 V indirectly-heated cathode, used as the "
            "first audio amp, plate detector or low-noise RF stage in "
            "1937–50s receivers and signal generators."
        ),
        "country": "Australia (AWV / RCA-Radiotron)",
        "first_introduced": "1937",
        "era": "1937 – late 1950s",
        "confidence_label": "Medium · code is handwritten on the carton sticker",
        "confidence_class": "medium",
        "function": "Sharp-cutoff RF / IF / detector pentode (octal)",
        "envelope": "ST / GT-shape",
        "envelope_detail": "ST or GT glass, top-cap control grid",
        "base": "Octal (8-pin)",
        "base_detail": "International octal with top-cap control grid",
        "heating": "Indirectly heated, 6.3 V, 0.3 A",
        "rating_1_label": "Max plate voltage",
        "rating_1_value": "300 V",
        "rating_2_label": "Mutual conductance",
        "rating_2_value": "~1.2 mA/V",
        "application_short": "Sharp-cutoff RF / IF / detector / first-AF without AGC",
        "applications_prose": (
            "Octal version of the 6C6 — fixed-gain RF pentode with low "
            "noise and a sharp cutoff, used as the first IF stage, as a "
            "plate-detector, or as a low-distortion audio voltage "
            "amplifier. Common in laboratory signal generators (e.g. "
            "BC-221 frequency meter) and in PA systems alongside the "
            "remote-cutoff 6K7."
        ),
        "direct_equivs": ["6J7G", "6J7GT", "VT-91"],
        "substitutes": ["6C6 (6-pin, pre-octal)", "6SJ7 (single-ended octal, no top cap)", "EF37A (8-pin)"],
        "value_range": "A$15 – A$30",
        "value_note": "NOS, boxed, single tube",
        "value_prose": (
            "Common and inexpensive. Premium for metal-envelope 6J7 "
            "(versus glass) and for JAN-CRC military variants. Used "
            "pulls A$5–12."
        ),
        "sources": [
            ("Radiomuseum.org — 6J7", "https://www.radiomuseum.org/tubes/tube_6j7.html"),
            ("Frank's Tube Data — 6J7 datasheet", "https://frank.pocnet.net/sheets/030/6/6J7.pdf"),
            ("The Valve Store (AU)", "https://thevalvestore.com.au/"),
        ],
    },
    {  # 010 — Super Radiotron 6J8G
        "id": "010", "filename": "010-radiotron-6j8g.html",
        "brand": "Super Radiotron", "code": "6J8G",
        "category": "Frequency converters",
        "function_tag": "Triode-heptode converter",
        "source": "boxes-1.jpeg", "crop": "entry-010-crop.jpeg",
        "svg_key": "octal",
        "lede": (
            "Octal triode-heptode frequency converter — combines a local "
            "oscillator triode and a heptode mixer in one envelope, the "
            "first-stage workhorse of late-1930s and 1940s superhet "
            "receivers. Australian-made by AWV under the Super Radiotron "
            "label."
        ),
        "country": "Australia (AWV / RCA-Radiotron)",
        "first_introduced": "1938",
        "era": "1938 – mid 1950s",
        "confidence_label": "Medium · code is handwritten on the carton sticker",
        "confidence_class": "medium",
        "function": "Triode-heptode frequency converter (mixer-oscillator)",
        "envelope": "G-shape (large ST)",
        "envelope_detail": "G-shape envelope, ~38 × 110 mm",
        "base": "Octal (8-pin)",
        "base_detail": "International octal, key-locked centre spigot",
        "heating": "Indirectly heated, 6.3 V, 0.3 A",
        "rating_1_label": "Max plate voltage",
        "rating_1_value": "250 V (heptode)",
        "rating_2_label": "Conversion conductance",
        "rating_2_value": "~0.55 mA/V",
        "application_short": "First-stage mixer / oscillator in superhet receivers",
        "applications_prose": (
            "Standard frequency converter in Australian valve receivers "
            "from the late 1930s through the war years — produces the "
            "intermediate-frequency signal by mixing the incoming RF "
            "with the local oscillator's signal, both happening inside "
            "the same envelope. AWA, Astor, Healing and HMV sets all "
            "used it. The miniature post-war successor is the 6BE6 "
            "(B7G heptode, separate oscillator stage) or the all-in-one "
            "6BE8."
        ),
        "direct_equivs": ["6J8", "ECH33 (European triode-heptode)"],
        "substitutes": ["6K8G (different pinout)", "6BE6 (B7G miniature heptode)", "ECH81 (B9A)"],
        "value_range": "A$20 – A$40",
        "value_note": "NOS, boxed, single tube",
        "value_prose": (
            "Slightly less common than the 6D6 / 6C6 family because each "
            "set only used one. Used pulls A$8–15. Boxed Australian-made "
            "examples carry a modest collector premium."
        ),
        "sources": [
            ("Radiomuseum.org — 6J8G", "https://www.radiomuseum.org/tubes/tube_6j8g.html"),
            ("Frank's Tube Data — 6J8G datasheet", "https://frank.pocnet.net/sheets/093/6/6J8G.pdf"),
            ("The Valve Store (AU)", "https://thevalvestore.com.au/"),
        ],
    },
]


def main() -> None:
    for e in ENTRIES_DATA:
        html = render(e, ENTRIES_DATA)
        (ENTRIES / e["filename"]).write_text(html)
        print(f"wrote entries/{e['filename']}  ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
