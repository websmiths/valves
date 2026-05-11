# Data sources for valve lookups

These are the references the skill leans on, in roughly the order to try them.
Each has strengths and gaps — knowing which to consult for which field saves
time and avoids junk data.

## Primary technical references

### Radiomuseum.org
URL pattern: `https://www.radiomuseum.org/tubes/tube_<code>.html` (lowercase).
The most reliable source for: function, base type, envelope, heater
voltage/current, dimensions, year first sourced, identical/equivalent types,
similar tubes, military designation. Pricing requires membership and is not
usable for the catalogue.

### Frank's Electron Tube Data Sheets
URL pattern: `https://frank.pocnet.net/sheets/`. Hosts manufacturer datasheet
PDFs (RCA, Sylvania, Mullard, GE, Brimar, etc.). Best for: absolute maximum
ratings, electrical characteristics, pinout diagrams, typical operating
conditions. Search via Google with `5Z3 site:frank.pocnet.net`.

### Duncan Amps Tube Data Sheet Locator (TDSL)
`http://tdsl.duncanamps.com/show.php?des=<code>`. A searchable database that
collates basic specs and links out to PDFs. Good fallback when Radiomuseum
is missing a tube.

## Australian market pricing

### The Valve Store
`https://thevalvestore.com.au/`. Quote AUD prices "NOS-boxed, single tube"
from this site where available. Pricing on NOS audio tubes is often higher
than US sources; reflect that in the value range.

### Evatco
`https://www.evatco.com.au/`. Another current AU stockist — useful for
cross-checking and for tubes The Valve Store doesn't list.

When neither has the tube, fall back to US sources (Tube Depot, Tubes &
More) and convert AUD with a rough 1.5× multiplier, then say "estimated".

## Background and applications

### Fuzz Audio
`https://fuzzaudio.com/discovering-the-timeless-legacy-of-vacuum-tubes` and
the rest of the Fuzz blog have good general-audience descriptions of valve
function and historical use — handy for the "Applications" prose.

### VinylSavor (Tube of the Month)
`http://vinylsavor.blogspot.com/`. Audiophile-leaning but rich on history
and audio applications.

### Wikipedia
`https://en.wikipedia.org/wiki/Vacuum_tube` and `..._receiving_tubes`.
Good for: the European/American code mapping (e.g. 6GW8 ↔ ECL86), socket
type explanations, base-type history.

## Equivalents / cross-reference tables

### "Tube equivalents" handlists
Search `"<code> equivalent" OR "<code> substitute"`. The handlists from
RCA, Sylvania, and the AWA Radiotron catalogues are often scanned and on
NJ7P or radiomuseum forum threads. Useful for confirming that, e.g., the
5Z3 = 5U4G electrically but on a different base.

### European-American mapping
A handful of common ones to remember:

| US (RMA)  | European (Mullard/Philips) | Function                 |
|-----------|-----------------------------|--------------------------|
| 6V6 (GT)  | EL90 (sort of)              | Beam tetrode output      |
| 6L6       | KT66                        | Beam tetrode output      |
| EL34      | 6CA7                        | Pentode output           |
| 12AX7     | ECC83                       | Twin triode audio        |
| 12AT7     | ECC81                       | Twin triode RF/audio     |
| 6GW8      | ECL86                       | Triode-pentode (audio)   |
| 6BM8      | ECL82                       | Triode-pentode (audio)   |
| 5Y3       | (no exact EU equivalent)    | Full-wave rectifier      |

When a box shows the European code, look up the US equivalent too and list
both as direct equivalents.

## Citing in entries

Every URL you actually relied on goes in the Sources footer of the entry,
in the order: Radiomuseum, Frank's datasheet, an AU stockist for price, then
any history/applications source.
