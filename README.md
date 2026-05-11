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

| # | Code        | Brand           | Type                                       | Source image    | Count |
|---|-------------|-----------------|--------------------------------------------|-----------------|-------|
| 001 | **5Z3**   | RCA             | Full-wave rectifier (UX4)                  | `boxes-1.jpeg`  | 1     |
| 002 | **80**    | Radiotron       | Full-wave rectifier (UX4, pre-octal 5Y3)   | `boxes-1.jpeg`  | 4     |
| 003 | **78**    | Radiotron       | Variable-mu RF/IF pentode (6-pin)          | `boxes-1.jpeg`  | 1     |
| 004 | **6D6**   | Super Radiotron | Variable-mu RF/IF pentode (6-pin)          | `boxes-1.jpeg`  | ≈ 5   |
| 005 | **6C6**   | Radiotron       | Sharp-cutoff RF / detector pentode (6-pin) | `boxes-1.jpeg`  | 1     |
| 006 | **6X5GT** | Radiotron       | Full-wave rectifier (octal, 6.3 V)         | `boxes-1.jpeg`  | 1     |
| 007 | **KT66**  | G.E.C.          | Beam-tetrode audio output valve (octal)    | `boxes-1.jpeg`  | 1     |

First-batch sweep through `boxes-1.jpeg` — covers the clearly-labelled
Radiotron / RCA / GEC boxes (~13 of the visible ~40). Remaining boxes —
Mullard, Brimar, the handwritten Miniwatt cartons, and the loose-tube
tubs — are deferred to a follow-up pass. See `outputs/boxes-1-tally.md`
for the master survey of this photo.

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

### Cross-references worth knowing

- **003 (78)** and **004 (6D6)** are direct electrical equivalents on the
  same 6-pin small base. They're catalogued as separate entries because
  the printed codes differ, but a single valve could substitute for
  either in service.
- **001 (5Z3)** and **002 (80)** are both directly-heated 5 V rectifiers
  on the UX4 base. The 5Z3 is the higher-current sibling (3 A filament,
  225 mA DC out) of the 80 (2 A filament, 125 mA DC out).

### Unaccounted boxes in `boxes-1.jpeg`

Roughly 27 boxes from this frame are not yet catalogued. The bulk are:

- Yellow Miniwatt / Marshall cartons with codes only readable in person
  (visible glimpses suggest 6X4G, EH35, ATP4, 6V6 family).
- Small white Mullard boxes (codes below the photo's legibility).
- One Brimar carton with an obscured code.
- Handwritten white-sticker boxes in the upper-left clump (one looks like
  "6J7", another "6J8G", one possibly "6V6GT" — all to confirm).
- The two plastic tubs of loose un-boxed tubes (not in scope for the
  box-photo catalogue, but worth a separate inventory later).

See [`outputs/boxes-1-tally.md`](outputs/boxes-1-tally.md) for the master
sweep that produced these numbers.

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
