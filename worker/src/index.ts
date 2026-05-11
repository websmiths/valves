/**
 * valves-submission Worker
 *
 * Accepts a multipart/form-data POST with an image + optional note + a
 * shared secret, and commits the files to src-images/submissions/ on
 * websmiths/valves via the GitHub Contents API. A GitHub Action then
 * processes the submission and opens a PR.
 */

interface Env {
  SUBMISSION_SECRET: string;
  GITHUB_TOKEN: string;
  GITHUB_REPO: string;
  GITHUB_BRANCH: string;
  ALLOWED_ORIGIN: string;
}

const MAX_IMAGE_BYTES = 5 * 1024 * 1024;
const MAX_NOTE_CHARS = 1000;
const ALLOWED_MIME = new Set(["image/jpeg", "image/png", "image/webp"]);

/**
 * Light sanitisation of the submitter's free-text note before we commit it
 * to the repo. This is belt-and-braces on top of the workflow-level
 * prompt-injection guard — it removes the cheap-shot escapes a hostile
 * note could use to break out of its container in either the prompt
 * (XML-style tag) or the PR-body code block (triple backticks).
 *
 * What we do NOT do here: try to "detect" injection by pattern. Pattern
 * lists are brittle and the workflow prompt already names the threat
 * category for Claude.
 */
function sanitiseNote(raw: string): string {
  return raw
    .slice(0, MAX_NOTE_CHARS)
    // Strip ASCII control chars (incl. NUL) except CR/LF/TAB — keeps
    // legitimate multi-line notes intact, removes hidden directives.
    .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, "")
    // Block escape from the workflow's <submitter_note> envelope.
    .replace(/<\/submitter_note>/gi, "</submitter_note ↵>")
    // Block escape from the PR body's fenced code block.
    .replace(/```/g, "´´´")
    .trim();
}

function corsHeaders(env: Env, origin: string | null): HeadersInit {
  const allow = origin === env.ALLOWED_ORIGIN ? origin : env.ALLOWED_ORIGIN;
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin",
  };
}

function json(body: unknown, status: number, env: Env, origin: string | null): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...corsHeaders(env, origin) },
  });
}

function u8ToB64(u8: Uint8Array): string {
  const CHUNK = 0x8000;
  let s = "";
  for (let i = 0; i < u8.length; i += CHUNK) {
    s += String.fromCharCode.apply(null, Array.from(u8.subarray(i, i + CHUNK)) as number[]);
  }
  return btoa(s);
}

function strToB64(s: string): string {
  return u8ToB64(new TextEncoder().encode(s));
}

function makeSubmissionId(): string {
  const iso = new Date().toISOString().replace(/[:.]/g, "-").replace("Z", "");
  const rand = crypto.getRandomValues(new Uint8Array(3));
  const hex = Array.from(rand).map((b) => b.toString(16).padStart(2, "0")).join("");
  return `${iso}-${hex}`;
}

function extFor(mime: string): string {
  if (mime === "image/jpeg") return "jpg";
  if (mime === "image/png") return "png";
  if (mime === "image/webp") return "webp";
  return "bin";
}

async function putContent(
  env: Env,
  path: string,
  contentB64: string,
  message: string,
): Promise<{ ok: true } | { ok: false; status: number; error: string }> {
  const url = `https://api.github.com/repos/${env.GITHUB_REPO}/contents/${path}`;
  const resp = await fetch(url, {
    method: "PUT",
    headers: {
      "Authorization": `Bearer ${env.GITHUB_TOKEN}`,
      "Accept": "application/vnd.github+json",
      "User-Agent": "valves-submission-worker",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      content: contentB64,
      branch: env.GITHUB_BRANCH,
    }),
  });

  if (resp.ok) return { ok: true };
  const text = await resp.text();
  // Sanitise — never echo the auth header or token back to the client.
  let snippet = text.slice(0, 200);
  try {
    const j = JSON.parse(text);
    if (j && typeof j.message === "string") snippet = j.message.slice(0, 200);
  } catch {
    /* ignore */
  }
  return { ok: false, status: resp.status, error: snippet };
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const origin = request.headers.get("Origin");

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(env, origin) });
    }
    if (request.method !== "POST") {
      return json({ ok: false, error: "method not allowed" }, 405, env, origin);
    }
    if (new URL(request.url).pathname !== "/") {
      return json({ ok: false, error: "not found" }, 404, env, origin);
    }

    let form: FormData;
    try {
      form = await request.formData();
    } catch {
      return json({ ok: false, error: "expected multipart/form-data" }, 400, env, origin);
    }

    const secret = form.get("secret");
    if (typeof secret !== "string" || secret !== env.SUBMISSION_SECRET) {
      return json({ ok: false, error: "forbidden" }, 403, env, origin);
    }

    const image = form.get("image");
    if (!(image instanceof File)) {
      return json({ ok: false, error: "image field missing or not a file" }, 400, env, origin);
    }
    if (image.size === 0) {
      return json({ ok: false, error: "image is empty" }, 400, env, origin);
    }
    if (image.size > MAX_IMAGE_BYTES) {
      return json({ ok: false, error: `image too large (max ${MAX_IMAGE_BYTES} bytes)` }, 400, env, origin);
    }
    const mime = (image.type || "").toLowerCase();
    if (!ALLOWED_MIME.has(mime)) {
      return json({ ok: false, error: `unsupported image type: ${mime || "unknown"}` }, 400, env, origin);
    }

    let note = "";
    const rawNote = form.get("note");
    if (typeof rawNote === "string") note = sanitiseNote(rawNote);

    const id = makeSubmissionId();
    const ext = extFor(mime);
    const imagePath = `src-images/submissions/${id}.${ext}`;

    const imageBytes = new Uint8Array(await image.arrayBuffer());
    const imageB64 = u8ToB64(imageBytes);

    const imageResult = await putContent(
      env,
      imagePath,
      imageB64,
      `submission: ${id} (image)`,
    );
    if (!imageResult.ok) {
      return json(
        { ok: false, error: `failed to commit image (${imageResult.status}): ${imageResult.error}` },
        502,
        env,
        origin,
      );
    }

    if (note.length > 0) {
      const notePath = `src-images/submissions/${id}.note.txt`;
      const noteResult = await putContent(
        env,
        notePath,
        strToB64(note),
        `submission: ${id} (note)`,
      );
      if (!noteResult.ok) {
        // Image committed but note didn't — return partial success so the
        // human reviewing the PR notices the note is missing.
        return json(
          {
            ok: true,
            submission_id: id,
            warning: `note failed to commit (${noteResult.status}): ${noteResult.error}`,
          },
          202,
          env,
          origin,
        );
      }
    }

    return json({ ok: true, submission_id: id }, 202, env, origin);
  },
};
