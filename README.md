# Valves — a catalogue project

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
└── README.md
```

`entries/` will grow as we work through the source photos. Each entry is a
single self-contained HTML file — open it in any browser; nothing to install.

## Current status

| # | Code        | Brand | Type                    | Source image    |
|---|-------------|-------|-------------------------|-----------------|
| 001 | **5Z3** | RCA   | Full-wave rectifier     | `boxes-1.jpeg`  |

This is the proof-of-concept entry. Once the format is approved we'll process
the rest of `boxes-1.jpeg` (~40 visible boxes including Radiotron 6D6 / 80 /
78, Mullard, Brimar, G.E.C., Marconi etc.) and then on through the wider
collection.

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
