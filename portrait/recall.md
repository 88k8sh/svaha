# /recall — optional local semantic-recall layer for Portrait

Execute immediately, no preamble.

> A **by-meaning** index over your Portrait corpus, so synthesis can pull candidate
> evidence semantically — not only by exact keyword. `/recall` **complements grep; it
> does not replace it.** grep is exact, transparent, and zero-dependency; recall is
> fuzzy and recall-oriented (it finds the passage that *means* the thing even when it
> never uses the word). Portrait uses **both** and cites from both.

It is **optional, opt-in, and local-only.** Nothing in Portrait — and nothing in
Svaha's core loop — depends on it. If it isn't set up, every other command
behaves exactly as it does today (it falls back to grep). Turning it on changes one
thing: synthesis and `/mirror` gain a second way to *find* candidate evidence before
they cite it.

The implementation is `portrait/recall/recall.py` (the METHOD that ships) +
`portrait/recall/requirements.txt`. Run it from the Svaha project root.

---

## Honest dependency disclosure — read this first

`/recall` is **not zero-dependency.** It has exactly **one real dependency: a light
local embedding model.** Disclosing this plainly is the point — do not pretend
otherwise.

- **Embedding model:** `fastembed` running `BAAI/bge-small-en-v1.5` — an ONNX model
  (~130 MB), **no torch, no GPU, no server, no daemon.** It turns text into vectors
  locally. Weights download once on first use and cache under
  `portrait/recall/.model_cache/` (gitignored).
- **Vector store:** `sqlite-vec` — a single-file SQLite extension. **No server, no
  Docker.** The index is one `.db` file.

One-line install:

```bash
pip install -r recall/requirements.txt
```

That is the whole footprint: two pip packages, one model download on first use, one
local `.db` file. No service runs in the background; nothing phones home.

**Fail-soft contract (hard).** If either dependency is missing, `recall.py` prints the
install command and a `use grep` note to stderr, then **exits 0** — it never crashes
the caller. So a Portrait run on a machine without the deps just uses grep, exactly as
it does today. There is no degraded or half-broken state: recall is either *available
and additive*, or *absent and invisible*.

---

## Privacy contract

The built index (`portrait/identity/recall.db`) holds **your real corpus content**
(chunked text from your chats, writing, work, and handoffs). It is therefore treated
exactly like the live portrait:

- **Local-only.** It is **gitignored** — see `portrait/.gitignore` (the `recall.db`
  lines + the `recall/.model_cache/` line). It never auto-leaves the machine; no
  upload, no cloud index, no telemetry. Embeddings are computed **locally** — text is
  never sent to an embedding API.
- **Ship the method, never the meal.** `recall/recall.py` and
  `recall/requirements.txt` are tracked (the *method*). The `.db` and the model cache
  are never committed (the *meal*). If you ever add another live recall artifact, add
  its ignore line in the same commit.
- **No new data class leaves.** Sharing a portrait still goes through Svaha's
  release gate, manually — recall changes nothing about that.

If `recall.db` is **not** matched by `portrait/.gitignore`, **stop and fix the fence
before indexing anything.**

---

## When to use it — and when grep is enough

`/recall` earns its one dependency only when **scale** makes exact-match miss things:

- **A large imported corpus** — hundreds/thousands of chat conversations or a big
  writing folder, where the passage you need uses *different words* than your query
  ("felt carried" vs. "stopped fighting it" vs. "let go"). grep needs the exact token;
  recall finds it by meaning.
- **A long Svaha history** — dozens of `_NEXT_NNN.md` handoffs across a year,
  where a behavioral pattern recurs in varied phrasing across many files. recall
  surfaces the semantically-near handoffs grep would only find with a lucky keyword.
  (recall indexes the loop corpus — `next/` and `30_LEDGER/` — automatically, so the
  operator-pattern evidence is searchable by meaning too.)

**Grep is the right tool — don't bother with recall — when:**

- the corpus is small (a few files, a handful of handoffs) — grep reads it all anyway;
- you know the exact term, name, path, ticker, or date — exact match is faster and
  fully transparent;
- you need an exhaustive, auditable "every occurrence of X" — grep is complete by
  construction; recall returns a *ranked candidate set*, not a guaranteed-complete one.

The mental model: **recall is for "find me the passages that mean this"; grep is for
"find me the passages that say this."** Synthesis wants both, because the said-it-
differently evidence and the say/do gaps both matter for an anti-Barnum portrait.

---

## Setup (one-time, opt-in)

1. **Install the dependency** (above):
   ```bash
   pip install -r recall/requirements.txt
   ```
2. **Point it at your corpus.** recall reads Portrait's existing manifest —
   `portrait/identity/sources.md` — for the `- path:` entries, and **always** also
   indexes the Svaha loop (`next/`, `30_LEDGER/`). Placeholder paths (`<...>`)
   are skipped. (Run `/portrait` first if `sources.md` doesn't exist yet — Step 0
   creates it from the template; the template's placeholder paths simply don't resolve,
   which is fine.)
3. **Build the index:**
   ```bash
   python3 recall/recall.py index
   ```
   This walks each resolvable path, chunks the text, embeds each chunk locally, and
   writes `portrait/identity/recall.db`. Re-run any time the corpus grows — it rebuilds
   from scratch for a clean, reproducible index.

To check whether the layer is usable, just run a query (or `index`): if the deps are
missing it prints the install line and exits 0; if no db exists, `query` says so and
points you to `index` (or grep). There is no separate `status` subcommand — absence is
reported by the command you actually run.

---

## Query (what synthesis calls)

```bash
python3 recall/recall.py query "<by-meaning question>" --k 8
```

Each result is a **citeable candidate**, not a finished claim:

```
[1] sim=0.742  /Users/<you>/exports/chat.json:2204
    <one-line snippet of the matched passage>
```

- `citation` is `file:line` — the absolute path plus the 1-based start line of the
  chunk, so the evidence is reproducible and the synthesizer can open it and read the
  surrounding context.
- `sim` is closeness in meaning (higher = nearer), **not** a confidence in the claim.
  Confidence is still assigned by the synthesis discipline (Step 2 of `/portrait`),
  after a human-meaningful read of the candidate.

**A recall hit is candidate evidence — it does not bypass the citation discipline.**
The synthesizer still reads the actual passage, decides whether it genuinely supports a
claim, maps the file back to its `<source-id>` in `sources.md`, marks `✓VERIFIED` /
`?INFERRED`, and writes the `evidence:` line. recall changes *how candidates are found*,
never the bar a claim must clear to be written. The Barnum test, the multi-source rule
for `✓VERIFIED`, and the falsifier requirement all still apply unchanged.

---

## How it wires into the rest of Portrait (optional, additive)

Both `/portrait` and `/mirror` check for `recall.db` and branch:

- **`recall.db` exists and deps are present** → synthesis pulls candidate evidence via
  `recall.py query` (semantic) **and** keeps its grep / structured reads (exact). Both,
  complementary. Recall hits become cited evidence under the normal discipline.
- **No `recall.db`, or deps missing** → fall back to grep **exactly as today.** No
  behavior change for small corpora. This is the default and the common case.

The check is mechanical: does `portrait/identity/recall.db` exist? If yes, run a query
and use its hits *in addition to* grep; if a query prints the install/fallback note
instead of results, the deps are missing — grep only. Never block a portrait run on
recall — a failed/absent recall layer degrades silently to today's behavior.

---

## What /recall never does

- **Never replaces grep.** It is additive. Exact, transparent, complete search stays
  grep's job; recall only adds by-meaning candidate-finding on top.
- **Never lets corpus content leave the machine.** The `.db` and the model cache are
  local-only and gitignored; no upload, no external embedding API, no telemetry. The
  model runs locally — embeddings are computed on this machine.
- **Never crashes a caller.** Missing deps / missing db → print the install line, signal
  grep-fallback, exit 0. Fail-soft, always.
- **Never lowers the citation bar.** A recall hit is candidate evidence; it still passes
  through the anti-Barnum discipline (markers, multi-source `✓VERIFIED`, falsifier,
  Barnum test) before it becomes a claim.
- **Never pretends to be zero-dependency.** The one embedding-model dependency is
  disclosed up front; "optional" means you can skip it, not that it's free.
- **Never claims completeness.** recall returns a *ranked candidate set*. For "every
  occurrence of X," use grep — it's complete by construction.

---

## Dependency / cost summary (one place, honest)

| | what | footprint |
|---|---|---|
| embed model | `fastembed` + `BAAI/bge-small-en-v1.5` (ONNX, no torch) | ~130 MB model, one-time download, cached under `recall/.model_cache/`, runs local |
| vector store | `sqlite-vec` (single-file SQLite extension) | one `.db` file, no server |
| install | `pip install -r recall/requirements.txt` | two pip packages |
| index | `python3 recall/recall.py index` | seconds-to-minutes on first build, scales with corpus |
| query | `python3 recall/recall.py query "..." --k N` | sub-second after the model loads |

No daemon, no Docker, no GPU, no cloud. One model, one db file. Skip it and Portrait
runs on grep exactly as before.
