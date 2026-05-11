# Valves — a catalogue project

**Live site:** <https://websmiths.github.io/valves/>

Cataloguing a collection of vintage vacuum tubes (valves) from photographs of
their original boxes. Each box code is identified, looked up, and turned into
a catalogue entry with manufacturer, type, key ratings, typical applications,
direct equivalents and substitutes, and an approximate market value.

## Repository layout

```
.
├── src-images/                         Original photographs of the collection
├── entries/                            One HTML page per valve type
├── index.html                          Catalogue index (GitHub Pages landing)
├── .claude/skills/valve-catalogue-entry/
│                                       Portable workflow for adding entries
└── README.md
```

`entries/` will grow as we work through the source photos. Each entry is a
single self-contained HTML file — open it in any browser; nothing to install.

## Adding entries with Claude Code

The repo bundles a skill at `.claude/skills/valve-catalogue-entry/` that
captures the full workflow — identifying codes from a box photo, looking up
the canonical references, producing a new HTML entry that matches the
existing style, and updating the index. Open this repo in Claude Code and
ask things like:

- "Catalogue the RCA 5Z3 in boxes-1.jpeg"
- "Process the rest of boxes-1.jpeg"
- "Add an entry for the 6GW8"

The skill auto-loads when those kinds of phrases come up. See
[`.claude/skills/valve-catalogue-entry/SKILL.md`](./.claude/skills/valve-catalogue-entry/SKILL.md)
for the workflow, the data fields it captures, confidence rules for
ambiguous codes, and the HTML template it writes against.

## Current status

| # | Code        | Brand           | Type                                            | Source image    | Count |
|---|-------------|-----------------|-------------------------------------------------|-----------------|-------|
| 001 | **5Z3**   | RCA             | Full-wave rectifier (UX4)                       | `boxes-1.jpeg`  | 1     |
| 002 | **80**    | Radiotron       | Full-wave rectifier (UX4, pre-octal 5Y3)        | `boxes-1.jpeg`  | 4     |
| 003 | **78**    | Radiotron       | Variable-mu RF/IF pentode (6-pin)               | `boxes-1.jpeg`  | 1     |
| 004 | **6D6**   | Super Radiotron | Variable-mu RF/IF pentode (6-pin)               | `boxes-1.jpeg`  | ≈ 5   |
| 005 | **6C6**   | Radiotron       | Sharp-cutoff RF / detector pentode (6-pin)      | `boxes-1.jpeg`  | 1     |
| 006 | **6X5GT** | Radiotron       | Full-wave rectifier (octal, 6.3 V)              | `boxes-1.jpeg`  | 1     |
| 007 | **KT66**  | G.E.C.          | Beam-tetrode audio output valve (octal)         | `boxes-1.jpeg`  | 1     |
| 008 | **6B7S**  | Radiotron       | Duo-diode pentode (det. + AVC + AF, 7-pin)      | `boxes-1.jpeg`  | ≈ 2   |
| 009 | **6J7**   | Super Radiotron | Sharp-cutoff RF/IF pentode (octal, top cap)     | `boxes-1.jpeg`  | 1     |
| 010 | **6J8G**  | Super Radiotron | Triode-heptode frequency converter (octal)      | `boxes-1.jpeg`  | 1     |

Second sweep of `boxes-1.jpeg` covers everything I could read with at
least medium confidence — adds the 6B7S duo-diode pentode, the octal
6J7 sharp-cutoff pentode and the 6J8G frequency converter. Catalogued
types now account for roughly 18 of the ~40 visible boxes; the
remaining ~22 are mostly handwritten Miniwatt yellow cartons and a few
white Mullard boxes whose codes aren't legible at the photo's
resolution. See [`outputs/boxes-1-tally.md`](outputs/boxes-1-tally.md)
for the master sweep.

`boxes-2.jpeg` and `boxes-3.jpeg` are two further submissions of the
same tray (the two uploads are byte-identical to each other). They show
the same arrangement of boxes as `boxes-1.jpeg` and don't resolve any
of the previously unreadable handwritten codes at higher confidence —
no new entries were added from these photos. The handwritten /
unreadable cartons listed under *Unaccounted boxes* below still need a
physical pass to identify.

## Verification flags

A running list of entries that warrant a physical check, and other things
worth knowing about the catalogue as it grows. Tick `[x]` once the
physical box has been confirmed against the entry.

### Codes to verify in person

- [ ] **007 — G.E.C. KT66.** Code is pencil-handwritten on the carton.
  Reading is consistent with "KT66" and matches the GEC product line, but
  this is by far the most valuable tube in the catalogue so far
  (≈ A$200–400 NOS singles vs. A$15–30 for the Radiotrons), so worth
  confirming the glass etch reads `KT66` and the base is the brown
  micanol material before relying on the valuation.
- [ ] **004 — Super Radiotron 6D6.** Handwritten code "6D6" / "g.u. 6D6"
  on Australian-AWV white stickers across ≈ 5 cartons. Recount to confirm
  five identical boxes (no mixed types).
- [ ] **005 — Radiotron 6C6.** Handwritten code "6C6" on the AWV white
  sticker. Confirm reading (the "C" could conceivably be a poorly-formed
  "D", which would make it another 6D6).
- [ ] **008 — Radiotron 6B7S.** Printed factory label reads "6B7S"
  cleanly — recorded as High confidence — but the leading "6" prints in
  a closed style that could be misread as "0". Worth confirming on the
  physical box. Roughly two cartons of this type.
- [ ] **009 — Super Radiotron 6J7.** Handwritten code "6J7" on a white
  carton sticker. Confirm reading — could conceivably be "GJ7" or "6J4"
  with a poorly formed digit.
- [ ] **010 — Super Radiotron 6J8G.** Handwritten "6J8G" on a white
  sticker. Confirm — adjacent "6D6" handwriting is similar enough that
  the "8" could be a "B" or "0". 6J8G is the most likely reading given
  era and label style.

### Cross-references worth knowing

- **003 (78)** and **004 (6D6)** are direct electrical equivalents on the
  same 6-pin small base. They're catalogued as separate entries because
  the printed codes differ, but a single valve could substitute for
  either in service.
- **001 (5Z3)** and **002 (80)** are both directly-heated 5 V rectifiers
  on the UX4 base. The 5Z3 is the higher-current sibling (3 A filament,
  225 mA DC out) of the 80 (2 A filament, 125 mA DC out).
- **005 (6C6)** and **009 (6J7)** are functionally equivalent
  sharp-cutoff RF/IF pentodes on different bases — the 6C6 on the
  pre-octal 6-pin small base, the 6J7 on the octal base. A 6C6→6J7
  socket adapter is a common vintage-radio repair item.
- **008 (6B7S)** is the duplex-diode pentode counterpart to the simpler
  6C6 / 6J7 — same era, same factory, but combines detector, AGC and
  first-AF into one envelope. Sets that use a 6B7 typically don't need
  a separate detector valve.

### Unaccounted boxes in `boxes-2.jpeg` and `boxes-3.jpeg`

`boxes-2.jpeg` and `boxes-3.jpeg` are re-photographs of the same tray
shown in `boxes-1.jpeg` (the two new files are byte-identical to each
other). The unaccounted boxes are the same set listed below for
`boxes-1.jpeg` — handwritten Miniwatt yellow cartons, small white
Mullards, the Brimar carton and a few handwritten white-sticker boxes.
No additional codes were resolvable from the new photos.

### Unaccounted boxes in `boxes-1.jpeg`

Roughly 22 boxes from this frame remain uncatalogued after the second
sweep — these are the ones whose printed or handwritten codes I
genuinely couldn't read from the photograph. They split into:

- **~6 yellow Miniwatt (Mullard Australia) cartons** with handwritten
  codes. Visible fragments suggest the codes start with "6A##", "6X##",
  "EH##" or "AZ##" — i.e. probably a mix of 6X4G rectifiers, EH35 audio
  pentode, AZ41 rectifier, and similar 1940s-50s Mullard types — but I
  can't disambiguate from the photo.
- **~2 small white Mullard boxes** with codes that fall below the photo's
  legibility threshold (one possibly "5Y3GT" or "EY51").
- **1 Brimar carton** with the code partly obscured by an adjacent box.
- **~3 handwritten white-sticker boxes** in the lower-left clump (one
  small box near the cylindrical wrapped tubes, two small white boxes
  near the Mullards).
- **2 plastic tubs of loose un-boxed tubes** — out of scope for the
  box-photo catalogue, but worth a separate inventory pass.
- **A cluster of cylindrical paper-wrapped tubes** (loose, no boxes;
  also out of scope).

See [`outputs/boxes-1-tally.md`](outputs/boxes-1-tally.md) for the
master sweep that produced these numbers.

## How entries are built

For each box in a source photo we capture:

- **Code** as printed on the box (with a confidence flag when the print is
  worn or handwritten and ambiguous).
- **Brand** and **country of origin**.
- **Function** (rectifier / triode / pentode / converter / etc.) and base
  type (octal, UX4, B7G, Noval / B9A …).
- **Heater specs and key ratings** from the manufacturer datasheet.
- **Typical applications** — what these were actually used in (broadcast
  receivers, guitar amps, TV tuners, HT power supplies …).
- **Equivalents and substitutes**, both direct (same electricals + base)
  and via adapter (same electricals, different base — e.g. 6GW8 ≡ ECL86).
- **Approximate market value** for NOS / boxed / used, in AUD.
- **A reference photo** of the valve itself.

Unreadable or missing codes are recorded as "unaccounted for" with the box
count, so the final tally always matches the photograph.

## Reference sources

- [Radiomuseum.org](https://www.radiomuseum.org/) — definitive tube database
- [Frank's Electron Tube Data Sheets](https://frank.pocnet.net/) — manufacturer datasheets
- [The Valve Store (AU)](https://thevalvestore.com.au/) — Australian market pricing
- [Fuzz Audio — vacuum tube history](https://fuzzaudio.com/discovering-the-timeless-legacy-of-vacuum-tubes)
