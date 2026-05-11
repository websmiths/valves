---
name: valve-catalogue-entry
description: Use this skill whenever the user wants to add a vintage vacuum tube (valve) to the project catalogue, identify a code from a box photograph, generate a new catalogue entry HTML page, or process a tray/batch of valve boxes from a source image. Triggers include phrases like "catalogue this valve", "what's this tube", "add an entry for", "identify the boxes in this photo", "process boxes-N.jpeg", "make a card for the 6GW8", or any mention of a valve code (e.g. 5Z3, 6V6, ECC83, EL34, ECL86, 6GW8) in the context of this project. Also use when the user wants to update the index page or status table after adding entries.
---

# Valve catalogue entry

A skill for cataloguing vintage vacuum tubes from photographs of their boxes.
Each entry is one self-contained HTML page that pairs the box scan with
manufacturer data, equivalents and substitutes, typical applications, and an
indicative market value. The catalogue lives in the repo as a static site
hosted on GitHub Pages.

## Repository conventions

```
.
├── src-images/                    Original photographs
├── entries/NNN-brand-code.html    One entry per valve type — three-digit zero-padded id
├── index.html                     Landing page that lists all entries
├── README.md                      Status table at top
└── .claude/skills/                This skill plus any future ones
```

Entry filenames are lowercase, dashes only, e.g. `001-rca-5z3.html`,
`002-radiotron-6d6.html`. The id increments across the whole catalogue, not
per source-image.

## End-to-end workflow

There are two modes the user will ask for. Figure out which from context:

**Single-box mode** — "make an entry for the RCA 5Z3 in boxes-1.jpeg". You
already know which box. Crop it, look it up, generate the entry, update the
index.

**Tray mode** — "process boxes-2.jpeg" or "go through the rest". You're being
asked to identify every box in a source image, group duplicates, tally
unreadable boxes, and emit one entry per distinct type with a count. See
`references/tray-mode.md`.

Both modes use the same per-entry pipeline below.

## Per-entry pipeline

### 1. Identify the box

View the source image with the Read tool. If the photo was taken sideways,
rotate it first — `scripts/rotate_if_needed.py SRC DEST` handles this. Then
crop tightly around the target box and save the crop to
`outputs/entry-NNN-crop.jpeg`. `scripts/crop_box.py` is the one-line helper.

Read the code, brand, country-of-manufacture text and any handwritten notation
on the box. Note any ambiguity — vintage RCA labels often print "Z" in a
style that looks like "2" (so 5Z3 reads as "523"), and handwritten codes
on white stickers vary widely. See `references/confidence-rules.md` for how
to assign a confidence level and when to flag a code as low-confidence.

### 2. Look up the canonical data

For each code, search the reference sources in this order — they're listed
with their strengths in `references/data-sources.md`:

1. **Radiomuseum.org** — definitive for function, base, heater, dimensions,
   equivalents, first year. Search `site:radiomuseum.org tube_<code>`.
2. **Frank's Electron Tube Data Sheets** (frank.pocnet.net) — manufacturer
   datasheet PDFs with the absolute ratings.
3. **The Valve Store (AU)** and similar — current Australian market pricing.
   Prefer AU sources because the collection is Australian.
4. **Wikipedia and tube-of-the-month blogs** — background and historical
   context.

Use WebSearch first, then WebFetch on the top result if you need detail
beyond what the search summary gives you. Capture every URL you actually
relied on — they go in the Sources footer.

### 3. Fill in the data model

Every entry captures these fields. Use "—" or "Unknown" for anything you
genuinely couldn't find; do not invent values.

| Field            | Notes |
|------------------|-------|
| Code             | As printed on the box, normalised (uppercase, no spaces) |
| Brand on box     | RCA, Radiotron, Mullard, Brimar, G.E.C., Marconi, etc. |
| Country          | Country of manufacture (not just the brand's HQ) |
| First introduced | Year the type was first specified |
| Era              | Range of years the type was in common use |
| Confidence       | High / Medium / Low — see confidence-rules.md |
| Function         | Rectifier / triode / pentode / converter / output / etc. |
| Envelope         | ST / GT / miniature 7-pin / miniature 9-pin (Noval) / metal etc. |
| Base             | UX4 / octal / B7G / B9A / loktal — pick from the SVG set |
| Heating          | "Directly heated filament, 5.0 V AC, 3.0 A" style |
| Heater drop      | For rectifiers only |
| Max plate V      | From the datasheet |
| Max DC out / Ia  | mA per plate for rectifiers, anode current for amps |
| Application      | One sentence on what the valve does in a circuit |
| Mil designation  | VT-XXX, CV-XXX if known |
| Mounting         | If notable (e.g. base-down for big rectifiers) |
| Direct equivs    | Same electricals AND same base |
| Substitutes      | Same electricals, different base — needs adapter or rewire |
| Approx value     | AUD range, NOS-boxed-single |

### 4. Generate the HTML

Read `assets/entry-template.html`. It's the canonical layout — match its
visual style exactly because the catalogue's value is partly that every
entry feels like the same artefact.

Replacement pattern: every variable is wrapped as `{{FIELD_NAME}}`. Do a
text-substitution pass (not a code-evaluating one — these are not f-strings,
just markers). Leave structural HTML alone.

For the box image, base64-encode the crop and substitute into
`{{BOX_IMAGE_B64}}`:
```
python3 -c "import base64; print(base64.b64encode(open('outputs/entry-NNN-crop.jpeg','rb').read()).decode())"
```

For the valve illustration, pick the SVG from `assets/svg-envelopes/` that
matches the envelope type (`st-ux4.svg`, `octal.svg`, `miniature-7pin.svg`,
`miniature-9pin-noval.svg`). Edit the label text in the SVG to the valve
code. If none of the bundled SVGs fit, generate one in the same visual
language — keep stroke widths, palette, and proportions consistent.

For the equivalents and substitutes pills, render only what applies. If a
valve has no direct equivalents, remove that pill row entirely rather than
leaving an empty heading.

Write the result to `entries/NNN-brand-code.html`.

### 5. Update the index and the README

`index.html` has a list at `<ul class="entries">` with one `<li>` per entry.
Insert a new `<li>` for this entry, sorted by id. Bump the entry count in the
`.stats` div. If this is the first entry for a previously unprocessed source
image, also remove that image from the "boxes pending" count.

`README.md` has a status table near the top — append a row with id, code,
brand, function, source image.

### 6. Stop and report

Tell the user what was added, with a relative link to the new file and to
`index.html`. Don't auto-commit unless asked — the user manages git from
their terminal.

## Visual style — don't drift

Every entry uses the same colour tokens defined at the top of
`entry-template.html`:

- `--bg` `#fafaf7`  page background (warm off-white)
- `--ink` `#1d1d1b`  primary text
- `--muted` `#6b6b66`  labels and meta
- `--line` `#d9d4c7`  borders
- `--accent` `#8a1c1c`  the valve code, the tag, links — a single warm red

Headers are tracked uppercase 11px in muted grey, body is 14px, the big
code in the title is 36px in accent red. Pills are 12px tabular numerals.
The two-column grid below the hero stays as `1fr 1fr` — don't introduce
three-column rows or full-width sections unless absolutely necessary, it
breaks rhythm across the catalogue.

If a future entry truly needs a section that doesn't exist in the template
(e.g. transmitting tubes with cooling notes), add it as a new col-section
in the same dl/dt/dd pattern rather than a free-form panel.

## What to flag back to the user

Flag in the chat reply AND in the durable `## Verification flags` section
of `README.md` (add a new ticked / unticked checkbox row per item). The
README section is the long-term record so a future pass can pick up where
this one stopped without re-reading the whole conversation.

Things worth flagging:

- Any code marked **Medium** or **Low confidence** — they may want to
  verify against the physical box. Add to "Codes to verify in person".
- Boxes you couldn't read at all — add to "Unaccounted boxes" with a
  brief description (e.g. "two yellow Mullard boxes in the top-left,
  codes obscured by shadow").
- Equivalents or pairings worth knowing (e.g. "78 and 6D6 are direct
  electrical equivalents"). Add to "Cross-references worth knowing".
- Pricing that has a wide spread or that you couldn't confirm — give a
  range in the entry and say where it came from in the Sources footer.
- High-value finds (anything > ~A$100 NOS) — flag for physical
  confirmation regardless of confidence level, because the cost of a
  mis-identification is high.

## Files in this skill

- `SKILL.md` — this file, the workflow
- `assets/entry-template.html` — the entry layout, with `{{placeholders}}`
- `assets/svg-envelopes/*.svg` — illustration snippets by base type
- `scripts/crop_box.py` — crop a region from a source image
- `scripts/rotate_if_needed.py` — rotate a sideways photo
- `references/data-sources.md` — where to look things up
- `references/confidence-rules.md` — confidence levels and unreadable codes
- `references/tray-mode.md` — full-photo batch workflow
