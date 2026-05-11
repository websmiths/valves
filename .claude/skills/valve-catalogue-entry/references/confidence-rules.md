# Confidence and unreadable codes

Every entry has a Confidence field. It tells the user how trustworthy the
identification is and whether they should physically check the box.

## The three levels

**High** (green pill) — The code is printed clearly by the factory, in
standard typography, with no ambiguity. The brand and code together
unambiguously match exactly one type in the references. Default to this
when there's nothing suspicious.

**Medium** (amber pill) — Use when one of the following is true:
- The code is handwritten on a sticker, even if you can read it.
- The print is faded or partly obscured but you're still confident.
- The character is stylised in a way that has a known visual ambiguity —
  the classic case is the RCA "Z" that prints like a "2", so 5Z3 reads as
  "523" on the box. List the alternative reading in a note on the entry.
- The brand name on the box is generic enough (just "RADIOTRON" with no
  manufacturer) that there's some chance it's a relabel.

**Low** (red pill) — Use when the code is genuinely ambiguous: a character
could be read two different ways, the box is heavily damaged, or the code
matches multiple distinct types and you've had to guess which one based on
era/brand. Always include a "What I read / what it could be" note when
confidence is Low.

## Unreadable boxes

When you cannot make out a code at all — fully occluded, faded beyond
recognition, missing label — do not create an entry. Instead, in your
report back to the user, include a line like:

> 3 boxes unaccounted for in `boxes-1.jpeg`:
> - Top-left: small yellow Mullard box, code hidden by adjacent boxes.
> - Right of centre: white Radiotron box, sticker torn off.
> - Bottom row: red box, brand partly visible (looks like Brimar), code obscured by shadow.

The goal is that the total entries + unaccounted = visible boxes in the
photo, so the user can grab the physical boxes to inspect.

## When two boxes have the same code

In tray mode you'll often see, e.g., four Radiotron 80 boxes. Create one
entry, set the `count` in the report, and note any visible differences
(different label generations, different country stamps). Don't create
duplicate entries for the same type.
