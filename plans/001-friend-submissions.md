# Plan 001 — Friend submissions: drop a photo, catalogue updates

**Status:** Draft, ready for build.
**Audience:** Claude Code, running in this repo on Julian's Mac.
**Goal:** A non-technical friend can visit an unlisted URL, drop a photo of
some valve boxes, optionally type a short note, hit Submit, and within a
few minutes a PR appears on `websmiths/valves` with new catalogue entries
generated from the photo. Julian reviews and merges; GitHub Pages publishes
the updated site.

## Architecture

```
Friend's browser                                         Pages site
  │                                                       ▲
  │ 1. visits /submit.html (unlisted URL)                 │
  │    resizes image client-side to ≤1.5 MB JPEG          │ 8. redeploys
  │    POSTs FormData{image, note, secret} to Worker      │    on merge
  ▼                                                       │
Cloudflare Worker (valves-submission-worker)              │
  │ 2. validates SUBMISSION_SECRET, image size, MIME      │
  │ 3. commits image  → src-images/submissions/           │
  │    commits note   → src-images/submissions/*.note.txt │
  │    (two commits via GitHub Contents API)              │
  │ 4. returns JSON {ok, submission_id, status_url}       │
  ▼                                                       │
GitHub repo websmiths/valves ─────────────────────────────┤
  │ 5. push to src-images/submissions/** triggers         │
  │    .github/workflows/process-submission.yml           │
  ▼                                                       │
GitHub Action runner                                      │
  │ 6. Anthropic Claude Code action runs                  │
  │    against .claude/skills/valve-catalogue-entry/      │
  │ 7. skill processes image, writes entries, updates     │
  │    index.html + README.md, opens PR                   │
  │  ─ Julian reviews, merges ──────────────────────► merge to main
```

PR-first is non-negotiable for v1 — Julian needs to be able to fix
misreads before they go live.

## Prerequisites — gather before you start

The user needs to provide these to the build agent. List them out and ask
the user to paste each one in once before you start writing files.

1. **`ANTHROPIC_API_KEY`** — already exists on another repo. Add it as a
   repo secret on `websmiths/valves` under Settings → Secrets and variables
   → Actions. Same key is fine.
2. **GitHub fine-grained PAT** — scope: this single repo, permissions
   `Contents: read & write`. Lives in the Cloudflare Worker as
   `GITHUB_TOKEN` secret, not in the repo.
3. **Cloudflare account** — create a Worker named `valves-submission`. The
   build agent should walk the user through `wrangler login` if they don't
   already have it.
4. **Submission secret** — generate one with
   `openssl rand -hex 16`. Stored as `SUBMISSION_SECRET` in Worker, and as
   a hidden field in `submit.html` (yes, it's visible in page source — see
   "Anti-abuse" below for why this is OK for the threat model).

## Files to create

```
.
├── submit.html                              The upload form (single self-contained HTML)
├── plans/001-friend-submissions.md          This file
├── worker/
│   ├── wrangler.toml                        Cloudflare Worker config
│   ├── package.json                         Just wrangler + types
│   └── src/index.ts                         Worker code (~80 lines)
└── .github/
    ├── workflows/process-submission.yml     Action triggered by submissions/**
    └── PULL_REQUEST_TEMPLATE/submission.md  PR body template
```

Don't put the Worker token or submission secret anywhere in the repo —
those live in Cloudflare's Worker secrets store and GitHub's Actions
secrets store respectively.

## Build sequence

Work through these in order. Each step has a verification gate; don't move
on until it passes.

### Step 1 — `submit.html`

A single-file page in the repo root, same visual language as `index.html`
(reuse the colour tokens and typography). Contents:

- Header in the catalogue's style — eyebrow "Submit a Photo", h1 "New
  boxes.", lede explaining what happens after they submit.
- A `<form>` with three fields:
  - `<input type="file" name="image" accept="image/*" required>` — opens
    the camera on mobile, file picker on desktop
  - `<textarea name="note" rows="3" placeholder="Optional — where did you
    find these? Anything we should know about the boxes?"></textarea>`
  - A hidden `<input type="hidden" name="secret" value="...">` populated
    with the SUBMISSION_SECRET at build time (or read from a `?key=...`
    query param if you want the secret out of the static HTML — see
    Anti-abuse below)
- Client-side image resize before submission: load into a canvas, scale
  longest edge to max 2000px, export as JPEG quality 0.85. Show a small
  "preparing image…" status. Bail out with an apology if the resized
  output is still >5 MB.
- Submit button. On click, POST FormData to the Worker URL (configurable
  via a `<meta>` tag or hardcoded).
- After response: show one of three states inline — Submitted (with the
  submission id and a "your entries will appear on the catalogue in a few
  minutes" note), Error, or Network failure with a retry button.
- A back-link to the catalogue.

Verification: open in a local browser, drop a test image. Confirm the
resized blob is reasonable size and the POST goes out (you can stub the
endpoint with a `httpbin.org/post` for now).

### Step 2 — Cloudflare Worker

Scaffold:
```bash
mkdir -p worker && cd worker
npm create cloudflare@latest -- --type=hello-world --no-git --no-deploy .
# or hand-write wrangler.toml + src/index.ts if you want it minimal
```

`wrangler.toml`:
```toml
name = "valves-submission"
main = "src/index.ts"
compatibility_date = "2025-05-01"

[vars]
GITHUB_REPO = "websmiths/valves"
GITHUB_BRANCH = "main"

# Secrets set via: wrangler secret put SUBMISSION_SECRET
# Secrets set via: wrangler secret put GITHUB_TOKEN
```

`src/index.ts` responsibilities:

1. Accept `POST /` with `multipart/form-data`. Reject any other path/method.
2. CORS: allow the Pages origin only. Reflect the Origin header if it's an
   exact match for `https://websmiths.github.io`.
3. Validate:
   - `secret` field equals `env.SUBMISSION_SECRET` → else 403.
   - `image` field is a File with MIME `image/jpeg|image/png|image/webp`
     and size 0 < n ≤ 5MB → else 400 with a friendly message.
   - `note` field is a string of length ≤ 1000 chars → else trim.
4. Generate a submission id: ISO timestamp (colons replaced with `-`) plus
   six chars of `crypto.getRandomValues`. E.g. `2026-05-11T05-30-42-a3f9c2`.
5. Base64-encode the image. Watch out: `btoa(String.fromCharCode(...arr))`
   blows the stack on big arrays — use a chunked encoder:
   ```ts
   function u8ToB64(u8: Uint8Array): string {
     const CHUNK = 0x8000;
     let s = '';
     for (let i = 0; i < u8.length; i += CHUNK) {
       s += String.fromCharCode.apply(null, Array.from(u8.subarray(i, i + CHUNK)));
     }
     return btoa(s);
   }
   ```
6. PUT the image to GitHub Contents API:
   ```
   PUT https://api.github.com/repos/${env.GITHUB_REPO}/contents/src-images/submissions/${id}.jpg
   Authorization: Bearer ${env.GITHUB_TOKEN}
   Accept: application/vnd.github+json
   User-Agent: valves-submission-worker
   body: {message, content (b64), branch}
   ```
   `message` should be `submission: ${id} (image)`.
7. If note is non-empty, PUT a second file `${id}.note.txt` with the
   note (UTF-8, base64-encoded). Commit message
   `submission: ${id} (note)`.
8. Return `{ ok: true, submission_id: id }` JSON, status 202 Accepted.
9. Catch any error from the GitHub API and return its status + a sanitised
   message — never leak the token.

Verification: deploy with `wrangler deploy`. Then from a terminal:
```bash
curl -X POST https://valves-submission.<account>.workers.dev \
  -F "secret=<SUBMISSION_SECRET>" \
  -F "note=test from julian" \
  -F "image=@src-images/boxes-1.jpeg"
```
Should return `{ok:true,submission_id:"..."}`. Check that the image and
note file appeared at `src-images/submissions/` on the main branch.

### Step 3 — GitHub Action

`.github/workflows/process-submission.yml`:

```yaml
name: Process valve submission

on:
  push:
    branches: [main]
    paths:
      - 'src-images/submissions/**'

concurrency:
  group: process-submissions
  cancel-in-progress: false

jobs:
  process:
    # Don't loop on commits the action itself made
    if: "!contains(github.event.head_commit.message, '[bot]')"
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Identify new submissions
        id: scan
        run: |
          # Find images that haven't been moved out of submissions/ yet
          # and capture the matching .note.txt files alongside them.
          # Emit a JSON list to step output for the next step to consume.
          # (Plan-of-action: write a small Python helper at scripts/list_submissions.py)

      - name: Run Claude Code with bundled skill
        uses: anthropics/claude-code-action@latest
        # Use the canonical action name; verify the latest stable tag
        # at https://github.com/anthropics/claude-code-action before pinning.
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            New submission(s) are sitting in src-images/submissions/.
            For each image file in that directory:
            1. If there's a matching .note.txt with the same basename,
               read it and treat its contents as the submitter's note.
               Surface that note in the PR body.
            2. Move the image into src-images/ with a sensible incrementing
               name (boxes-2.jpeg, boxes-3.jpeg, …). Delete the corresponding
               .note.txt after capturing its contents.
            3. Use the bundled valve-catalogue-entry skill — its SKILL.md is
               at .claude/skills/valve-catalogue-entry/SKILL.md — to identify
               every box in the image and create entries. Tray mode is
               appropriate.
            4. Update index.html (entries by category, stats) and README.md
               (status table).

            Do not commit. Stage everything and let the next workflow step
            open a PR.

      - name: Open pull request
        uses: peter-evans/create-pull-request@v6
        with:
          commit-message: "submission: process ${{ steps.scan.outputs.summary }} [bot]"
          branch: submission/${{ github.run_id }}
          title: "Submission: ${{ steps.scan.outputs.title }}"
          body-path: .github/PULL_REQUEST_TEMPLATE/submission.md
          labels: submission
          delete-branch: true
```

Notes for whoever implements this:
- The exact name and version of Anthropic's GitHub Action may have changed.
  Check the README at https://github.com/anthropics/claude-code-action and
  use whatever the current setup pattern is.
- The action needs the working directory to be the repo checkout (it is by
  default).
- The `scan` step is described loosely — feel free to do it inline in bash
  if a Python helper feels overkill. The action only needs to know what
  image filenames it's dealing with.

Verification: trigger by manually dropping a test image into
`src-images/submissions/` via the GitHub web UI, push to main. Confirm the
workflow runs, opens a PR, and the diff contains new entry HTML.

### Step 4 — PR template

`.github/PULL_REQUEST_TEMPLATE/submission.md`:

```markdown
## Submission

**Submitted:** {{ submission timestamp from filename }}
**Image:** {{ new src-images/boxes-N.jpeg }}
**Submitter's note:** {{ note text, or "(none)" }}

### Boxes identified

{{ Claude fills this in: a bullet list of code, brand, confidence }}

### Confidence flags

{{ Any Medium / Low confidence entries that warrant a look }}

### Unaccounted-for boxes

{{ Boxes that couldn't be read, with brief location notes }}

---

Generated by the valve-catalogue-entry skill. Review the diff, fix any
misreads inline, then merge to publish. The Pages site redeploys
automatically on merge.
```

The action's prompt should be tweaked to fill in these sections so the
template is meaningful — alternatively, generate the PR body
programmatically in a step before `create-pull-request` and pass it via
`body:` instead of `body-path:`.

### Step 5 — Wire it all together

1. Deploy the Worker. Note its URL.
2. Hardcode that URL in `submit.html` (or set it via a `<meta>` tag and
   read in JS — either is fine, the Worker URL is not secret).
3. Add the `ANTHROPIC_API_KEY` secret to the repo if not already present.
4. Push everything to `main`. Pages will redeploy with `/submit.html`
   available at https://websmiths.github.io/valves/submit.html.

## Smoke test

End-to-end, with two test cases. Run both before declaring done.

**Test 1 — happy path with a known photo:**
1. Open `/submit.html` in a fresh browser session.
2. Submit `boxes-1.jpeg` (the existing one) with note "smoke test".
3. Worker returns 202 with submission id.
4. Within 30s, a commit appears on main under `src-images/submissions/`.
5. Within ~3 minutes, the Action completes and a PR opens.
6. PR body contains the note "smoke test" and a sensible list of boxes.
7. Close the PR without merging — we don't want duplicate entries.
8. Manually delete the test submission files from main.

**Test 2 — wrong secret:**
1. Edit `submit.html` to send a wrong `secret` value.
2. Submit. Confirm Worker returns 403 and nothing lands in the repo.

## Anti-abuse — threat model

The threat is not a determined attacker — it's web crawlers and the chance
that the URL ends up shared somewhere it shouldn't. Defences in order of
cost-to-attacker:

1. **Unlisted URL.** Don't link `/submit.html` from `index.html`. Give the
   friend the URL directly via text. This eliminates 95% of risk.
2. **Shared secret.** Visible in page source but invisible to a crawler
   that hasn't found the page. Anyone who finds the URL can scrape the
   secret, so this is bypass-able with effort.
3. **Worker-side rate limit.** Cloudflare has free per-IP rate limiting —
   add a rule like 5 requests/minute. This stops automated abuse cold.
4. **GitHub PAT scope.** The token can only write to this one repo's
   contents. Worst case: someone fills `src-images/submissions/` with
   junk. You revert and revoke the PAT in 30 seconds. No data leakage,
   no code execution.
5. **Optional Cloudflare Turnstile.** Their free CAPTCHA. Three lines in
   the form, one extra check in the Worker. Add later if abuse appears.

This is enough for v1. Revisit if traffic patterns suggest you need more.

## Operational notes

**Costs.** Worker free tier: 100k requests/day. GitHub Actions free tier
on public repos: unlimited. Anthropic API: ~$0.10-0.30 per submission
depending on web-search count. Realistic monthly spend if the friend
submits weekly: under a dollar.

**Rotating secrets.** If the SUBMISSION_SECRET leaks: generate a new one,
update Worker via `wrangler secret put`, update `submit.html`, push. If
the PAT leaks: revoke at GitHub Settings → Developer settings, generate a
new one, `wrangler secret put GITHUB_TOKEN`.

**Monitoring.** `wrangler tail` streams Worker logs in real time during
development. For ongoing monitoring, Cloudflare's dashboard shows
request counts and error rates. GitHub Actions emails Julian on failure
by default.

**What happens if Claude misreads.** Julian fixes in the PR before
merging. If it's already merged, fix on `main` directly — same workflow
as any other catalogue edit.

## Out of scope for v1 — possible follow-ups

- **Submitter-facing status page.** Currently the friend just trusts that
  it'll work and checks the catalogue in a few minutes. A status page
  keyed by submission_id would be nice but adds infra.
- **Email notification to the friend on publication.** Worker could send
  via a transactional email provider (Postmark, Resend) once we have an
  email address for them.
- **Multiple-image submissions.** Currently one image per submission. If
  the friend wants to send a whole batch, they upload N times.
- **Friend attribution in entries.** Could add an "attribution" field to
  the data model (e.g. "Submitted by Dave, May 2026") and surface it in
  the entry footer.
- **Skill improvement loop.** After a few real submissions, audit where
  the skill misread and update SKILL.md / references accordingly. Worth
  doing before the catalogue grows past ~50 entries.

## Definition of done

- A test submission from a fresh browser, with an image and a note,
  results in an open PR on `websmiths/valves` within 5 minutes.
- The PR body shows the note and a sensible boxes-identified summary.
- Merging the PR causes the new entries to appear at
  https://websmiths.github.io/valves/ within Pages' usual deploy time.
- Bad secret submissions are rejected and leave no trace in the repo.
- Documentation: `submit.html` mentions the catalogue and links back;
  `README.md` has a short section on how submissions work (without
  exposing the secret URL).
