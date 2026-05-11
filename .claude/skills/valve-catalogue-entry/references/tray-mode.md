# Tray mode — processing a whole source image

When the user asks to process an entire photo (rather than one specific
box), the workflow is:

## 1. Get the photo oriented

Run `scripts/rotate_if_needed.py` if needed. Save the rotated version to
`outputs/<source>-rotated.jpeg` and use that for the sweep.

## 2. Sweep systematically

Pick rows or columns based on how the boxes are arranged. Work left-to-right,
top-to-bottom. For each box, write a single-line tally entry:

```
row 1, col 1: Radiotron 6D6  (Australian, printed, High)
row 1, col 2: Super Radiotron 6B7S  (Australian, printed, High)
row 1, col 3: Marshall 6J7G handwritten  (Medium)
...
```

This list is the master record. Save it to `outputs/<source>-tally.md`.

## 3. Collapse duplicates

Group identical codes together with a count. Keep at least one bounding-box
reference per group so a future pass can find a representative.

```
- Radiotron 6D6 × 5  (rows 1-3)
- Radiotron 80 × 4  (row 4)
- RCA 5Z3 × 1  (row 4, col 5)
- Marshall 6J7G × 2  (rows 2-3, handwritten, Medium confidence)
...
- Unaccounted × 3  (see notes)
```

## 4. Generate entries

For each distinct code, run the per-entry pipeline from `SKILL.md`. Reuse
the source-image crop for the first occurrence; subsequent boxes of the
same type don't need their own crop.

When updating the entry, include the count in the README status table and
mention it in the entry's Identification block as a small note like
"5 boxes present in source image".

## 5. Cross-check the total

After processing, the sum of (entries × their counts) + unaccounted should
equal the visible-box count from step 2. If it doesn't, you missed
something or double-counted — go back to the tally.

## Pacing

A tray of 40 boxes is a lot. Don't try to do every entry in one session.
A sensible pace is: full tally + duplicate collapse in one pass, then 5-10
entries per follow-up batch. The skill is fine to invoke incrementally.
