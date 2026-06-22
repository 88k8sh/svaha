# /portrait — Evidence-Anchored Becoming Portrait

Execute immediately, no preamble. Do not ask for confirmation before reading.

> The synthesis method behind the Portrait layer. See `portrait/README.md` for what
> Portrait is and how it sits inside Svaha; this file is the **how** — the prompt
> that ingests your corpus and your decision-history and writes (or updates) an
> evidence-anchored, longitudinal portrait. Pure prompt/method: it runs locally in
> Claude Code, reads only local files, and writes only local files. Nothing uploads.

Portrait is an **optional, opt-in bolt-on**. Nothing in Svaha's core loop depends on
it. It is **off until you run this command.**

It produces two things every run:
1. updates `portrait/identity/PORTRAIT.md` — the **current synthesis** (the living "read-me" face), and
2. mints a new frozen dated snapshot `portrait/identity/portraits/_PORTRAIT_NNN.md`.

The **becoming-arc is the diff across snapshots.** You never rewrite an old one — same
frozen-numbered-snapshot discipline as the `_NEXT_NNN.md` handoff loop.

---

## Privacy contract — read this first, it gates everything below

This command reads **real personal data** (your corpus + your decision-history) and writes
**real inferences about you**. Both are local-only.

- **Ship the method, never the meal.** Only `*.template.md` files under `portrait/identity/`
  are tracked in git (the format, the seeds, the placeholders — zero personal content). The
  *live* artifacts this command writes are **`.gitignored`** and never committed:
  `identity/PORTRAIT.md`, `identity/portraits/*.md`, `identity/disputed.md`,
  `identity/sources.md`. The fence is already wired — see `portrait/.gitignore`. **Do not
  weaken it, and do not write personal content into any `*.template.md` file.**
- **Local-first (hard).** Corpus and portraits live on this machine and **never auto-leave
  it.** No upload, no cloud profile, no telemetry. Reading a chat export from a local path is
  fine; sending corpus text or portrait content to any external service is not. If the user
  ever asks to *share* a portrait, that is a deliberate, separate, manual act — it goes
  through Svaha's release gate (an outbox + manual review), never automatically.
- **No hard deletes.** A superseded `PORTRAIT.md` is archived before being overwritten (Step 6),
  never destroyed. Frozen snapshots are never edited or deleted — the pass number is the history.

If any live artifact named above is **not** matched by `portrait/.gitignore`, **stop and fix
the fence before writing anything.** A new live artifact type added without an ignore line is
a privacy leak waiting to be committed. (The optional `/recall` layer adds one more such
artifact — `identity/recall.db`, which holds chunked corpus content — already fenced; if you
ever rename or relocate it, re-fence it in the same change.)

---

## What this command is — and the one boundary it never crosses

**Mirror, not mask.** Portrait describes you **to yourself**. It is a reflection you read,
argue with, and revise. It is **not** a clone, an agent, a persona, or a voice-imitator —
it never produces an artifact whose purpose is to *act or speak as you to other people*.
That is the opposite lane (the Second Me / WeClone clone-builders), and Portrait refuses it
by design. If a run would produce anything that imitates the user *outward*, stop — that is
out of scope. The only audience for a portrait is the person it is about.

**Anti-Barnum is the core discipline, not a feature.** The standard failure of every tool in
this genre is the horoscope effect — vague, flattering, universally-true statements that feel
personal but apply to anyone (the Forer effect). Portrait fights this **structurally**: every
single claim carries a citation to the specific corpus evidence that produced it, a verification
marker, and a confidence. A claim you can't trace to evidence is a claim you delete. The whole
portrait is built to be **falsifiable and disputed** — see the anti-Barnum guarantees enumerated
at the end of this file.

---

## Step 0 — First-run setup (skip on repaint)

Check for `portrait/identity/PORTRAIT.md` and `portrait/identity/sources.md`.

- **If both exist** → this is a repaint. Skip to Step 1.
- **If either is missing** → first run. Seed the live files from their tracked templates,
  then walk the user through pointing at their corpus:

  ```
  cp portrait/identity/PORTRAIT.template.md            portrait/identity/PORTRAIT.md
  cp portrait/identity/sources.template.md             portrait/identity/sources.md
  cp portrait/identity/disputed.template.md            portrait/identity/disputed.md
  cp portrait/identity/portraits/_PORTRAIT_001.template.md  portrait/identity/portraits/_PORTRAIT_001.md
  ```

  (If a template is missing, create the live file from the format defined in this spec —
  don't block on a missing seed.)

  Then **interview the user once** to populate `portrait/identity/sources.md` — the corpus
  manifest. Ask for local paths only (never ask them to upload). Suggested prompts:
  - "Where are your chat exports?" — ChatGPT (`conversations.json`), Claude exports, etc.
  - "Where's your own writing?" — a notes/essays/journal folder, Obsidian vault, drafts.
  - "Where's your work product?" — repos, docs, a projects directory.
  - Confirm the Svaha decision-history sources are present (Step 1.B finds them automatically).

  Record each source in `sources.md` as `label → absolute path → kind (chat|writing|work) →
  date-range (if known)`. This manifest is what makes every later citation reproducible.

Announce: `portrait: first run — seeded live files, manifest at identity/sources.md.`

---

## Step 1 — Read the two source layers (the differentiator is layer B)

Portrait synthesizes from **two corpora at once.** Read both before writing anything.

**Optional semantic candidate-finding (recall) — additive, fail-soft.** Before searching,
check the optional `/recall` layer (full spec: `portrait/recall.md`):
- if `portrait/identity/recall.db` **exists** → for each corpus layer below, pull candidate
  evidence **both** ways: `python3 recall/recall.py query "<by-meaning probe>" --k 8`
  (semantic — finds passages that *mean* the thing in different words) **and** your usual
  grep / structured file reads (exact — names, dates, terms, complete occurrence sets). They
  are complementary; use both and merge the candidates. If a query prints the install/grep-
  fallback note instead of results, the deps are missing → grep only.
- otherwise (no db, or deps missing) → **fall back to grep exactly as today.** No behavior
  change. recall is opt-in; never block a run on it (it fails soft, exit 0).

A recall hit is **candidate evidence, not a finished claim** — its `file:line` citation maps
back to a `<source-id>` in `sources.md`, so it's directly citeable, but it still passes through
the full citation discipline below (read the passage, decide if it supports the claim, mark
`✓VERIFIED`/`?INFERRED`, write the `evidence:` line). recall changes *how candidates are
found*; it never lowers the bar a claim must clear. Use recall for large corpora and long
handoff histories where grep misses by-meaning; for a small corpus, grep alone is enough.

### A. Imported corpus — what you *said*

From the paths in `portrait/identity/sources.md`, read the user's own material:
- **Chat exports** — ChatGPT / Claude / other LLM conversations. These are the densest source:
  years of how the user thinks out loud, what they return to, what they ask for over and over.
- **Personal writing** — essays, notes, journal entries, drafts. The user's voice unmediated by a prompt.
- **Work product** — code, docs, projects. What they actually build and how.

For a large corpus, **sample with a stated method** rather than claiming to read everything you
didn't: read date-stratified slices (early / middle / recent) so the *arc* is visible, plus any
files the user flags. **Say what you sampled** — an honest "read 40 of ~600 conversations,
stratified across 2023–2026" beats a false "analyzed your whole corpus." Never assert coverage
you don't have (this is the `✓VERIFIED` / `?INFERRED` honesty applied to your own reading).

### B. The Svaha loop itself — what you *do* (the input nothing else has)

This is the structurally-unique source. Journaling and chat tools can read what you *said*;
only Svaha has been recording how you actually *operate over time*. Read all three:

1. **The frozen handoffs** — every `portrait/../next/_NEXT_NNN.md` (i.e. `<system-dir>/next/`).
   Each is a frozen snapshot of how a real session ended: what you set out to do, what
   succeeded/failed (the `outcome:` field), the strategies that `worked:` / `failed:`, what you
   carried forward vs. dropped. **The sequence of these is a behavioral record** — what you
   start, what you finish, what you abandon, what you return to, how your stated plans compare
   to what actually landed.
2. **The conviction-vs-outcome calibration record** — cross-reference the conviction tags
   attached to decisions (the `conviction: high|medium|low` language from `CLAUDE.md`'s Operator
   layer) against the **verified outcomes** the next boot recorded. A `high`-conviction call that
   later verified `FAILED` is a **calibration miss**; a pattern of them is a real, evidenced trait
   ("over-confident on X-shaped decisions"). A well-calibrated track record is equally a finding.
   Sources: the `_NEXT` header `outcome:` fields, `30_LEDGER/session-fixes.md`,
   `30_LEDGER/LESSONS.md`, and `30_LEDGER/CHANGELOG.md`.
3. **The promoted corrections** — the rules that got written into `CLAUDE.md` (and the lessons in
   `30_LEDGER/LESSONS.md`) because a behavior recurred. Each promoted rule is **evidence of a
   mistake the user makes often enough that the system had to harden against it.** The 2-strike
   promotion path means a promoted rule is, by construction, a *repeated* pattern — high-signal.

**Treat layer B as first-class, not a footnote.** A portrait that draws only on layer A is just
another chat-recap. The decision-track-record is what makes this a portrait of *who you are as an
operator*, which is the part no competitor can reproduce without a context-OS underneath it. Where
layer A and layer B **agree**, you have your strongest `✓VERIFIED` claims (said *and* done). Where
they **disagree** — you talk like X but operate like not-X — that gap is one of the most valuable
things a mirror can show, so surface it explicitly as a tension (Step 2).

Announce: `portrait: read corpus [N chat / M writing / K work, stratified <range>] + decision-history [J handoffs, calibration record, P promoted rules].` — and, if recall was used, append `· recall: on (semantic + grep)`; if not, the line stands as-is (grep only, no recall mention needed).

---

## Step 2 — Synthesize: who you ARE and who you are BECOMING

The portrait is an **arc**, not a snapshot type. Frame the person across these dimensions —
but **derive the structure from the evidence**, don't force the user into a fixed template of
traits (that's how Barnum creeps back in). Use these as lenses:

- **Stable core** — identity-domains that hold steady across the whole corpus and the whole
  handoff history. What has been true the entire time. (`✓VERIFIED` by definition — it shows up
  across many sources and dates.)
- **In-flux / becoming** — domains visibly *moving*: a shift in what they work on, a value they're
  reweighing, a stance that softened or hardened, a skill they're deliberately building. The
  **direction** matters as much as the current position — name where it's trending and the
  evidence for the trend (early-corpus vs. recent-corpus contrast; an explicit decision in the
  handoffs).
- **Growth themes** — the throughlines of the becoming: what the person is repeatedly trying to
  become better at, across both what they say and what they do.
- **Unresolved tensions** — genuine contradictions held in the evidence: a stated value vs. a
  revealed preference, a high-conviction self-image vs. a calibration record that disagrees, two
  drives that pull opposite ways. **Do not resolve these artificially.** A held tension named
  honestly is worth more than a tidy resolution that flattens the person. The say/do gaps from
  Step 1.B belong here.
- **Operator profile (from layer B only)** — how they actually behave under uncertainty: what they
  start vs. finish, where conviction is well-calibrated vs. systematically off, the mistakes that
  recurred often enough to become rules. This section is the differentiator; it cannot exist in a
  tool that hasn't been recording decisions-with-outcomes.

**The hard rule for every claim — no exceptions:**

> Every claim in the portrait carries (a) the **evidence** that produced it — a short quote or a
> faithful paraphrase, **plus its source** (which file / which handoff / which date-slice), (b) a
> **verification marker**, and (c) a **confidence**.

Verification markers (the same ones defined in `CLAUDE.md`):
- **✓VERIFIED** — corroborated by **multiple independent sources** (e.g. shows up in the writing
  *and* the handoffs; appears across several date-stratified slices). Strong.
- **?INFERRED** — a single source, or a weak/indirect reading. The user can dispute it. This is the
  honesty marker — use it generously rather than over-claiming `✓VERIFIED`.

Confidence: `high | medium | low`, reflecting how much evidence and how consistent it is.

**Claim format** (use consistently so the portrait is scannable and disputable):

```
- [✓VERIFIED · high] <the claim, stated plainly and specifically>
    evidence: "<quote or tight paraphrase>" — <source: file / _NEXT_NNN / date-slice>
              "<a second corroborating source, for ✓VERIFIED>" — <source>
    falsifier: <what observation would prove this wrong> — so the user can argue with it
- [?INFERRED · low] <a claim from a single thin source>
    evidence: "<quote>" — <source>
    falsifier: <what would disconfirm it>
```

**Anti-Barnum — the banned move.** Before writing any claim, run the **Barnum test**: *"Would this
sentence be true of most thoughtful people?"* If yes, it is a horoscope line — **delete it or make
it specific enough to be wrong.** Concretely banned:
- Vague flattery: "you're insightful," "you care deeply," "you have a rich inner life."
- Universal traits dressed as personal: "you value authenticity," "you're hard on yourself,"
  "you crave both stability and freedom," "you can be your own worst critic."
- Any claim with no citation. **No evidence → no claim.** Not "low confidence" — *deleted.*
- Resolved-tidy contradictions that flatten a real tension into a comfortable both-and.

A good portrait line is one the user could read and say **"no, that's wrong"** — and point to why.
If nothing in the portrait is disputable, it has failed the discipline.

---

## Step 3 — Diff against the last snapshot (the becoming-arc)

Read the most recent `portrait/identity/portraits/_PORTRAIT_<NNN>.md` (the highest-numbered live
snapshot; if only the template seed exists, this is the first real portrait — note that and skip
the delta). Produce a `## Delta since _PORTRAIT_<NNN>` block, 2–6 bullets:
- what **settled** (was `?INFERRED`, now `✓VERIFIED` with new corroboration),
- what **shifted** in the in-flux domains (direction of movement + the new evidence),
- what is **newly grounded** (a domain the prior portrait couldn't evidence),
- what the user **disputed** since last time — read every `OPEN` `D-NNN` block in
  `identity/disputed.md` (Step 5) and account for each: flip it to `RESOLVED` (re-grounded
  with stronger evidence, or narrowed/downgraded) or `DROPPED` (removed; 2nd strike →
  add its pattern to the Distrusted-patterns rollup). No `OPEN` dispute may survive a repaint.

The delta is the literal becoming-arc. It is the thing no one-shot personality-type produces.

---

## Step 4 — Write the current synthesis + mint the frozen snapshot

Two writes, in this order, with an archive in between (Step 6 covers the archive).

**A. Update the current synthesis** → `portrait/identity/PORTRAIT.md`.
This is the living "read-me" face — the portrait as it stands *now*, always mirroring the latest
synthesis. Status `current`. It carries the full evidence-anchored body from Step 2 plus the Step-3
delta. Overwrite-in-place (after archiving the prior version — Step 6).

**B. Mint a new frozen snapshot** → `portrait/identity/portraits/_PORTRAIT_<NNN+1>.md`.
Same body, frozen. `<NNN+1>` is zero-padded 3-digit (`001`→`002`…, auto-expand past `999`). This is
the immutable dated point in history. **Never edit a prior snapshot** — the snapshot number is the
version control, exactly like `_NEXT_NNN.md`.

Frontmatter on the frozen snapshot:

```yaml
---
id: portrait-snapshot-<NNN+1>
snapshot: <NNN+1>
created: <TODAY>
supersedes: _PORTRAIT_<NNN>
sources_read: <one line — what corpus + decision-history this pass drew on, with sample method>
status: frozen
layer: portrait
release_status: local-only
---
```

Frontmatter on `PORTRAIT.md` (the derived present — no `snapshot:`/`supersedes:`):

```yaml
---
id: portrait-current
created: <TODAY>
latest_snapshot: <NNN+1>
status: current
layer: portrait
release_status: local-only
---
```

Keep the section shape identical across snapshots so any two passes diff cleanly side by side.

---

## Step 5 — Leave the dispute channel open (anti-Barnum, made operational)

A mirror you can't argue with is a horoscope. After writing, tell the user plainly:

```
portrait: every claim is marked ✓VERIFIED / ?INFERRED with its evidence and a falsifier.
Dispute any line — tell me which claim is wrong and why, and I'll log it to
identity/disputed.md. Disputed claims are revisited on the next /portrait run (Step 3):
removed, downgraded, or re-grounded with stronger evidence.
```

When the user disputes a claim, append it to `portrait/identity/disputed.md` (a single
**append-only** log — not a numbered snapshot; it accumulates over time). Use the **one
canonical block format** defined in `disputed.template.md` and `mirror.md` — a numbered
`D-NNN` entry with an explicit status (`OPEN` → `RESOLVED`/`DROPPED`) and a strike count:

```
### D-<NNN>  (OPEN)  — <YYYY-MM-DD>
- claim disputed: "<the exact claim text the user pushed back on>"
- shown in: PORTRAIT.md §<section> / snapshot _PORTRAIT_<NNN>
- reason: <wrong | overreaching | outdated>
- user note: "<one line in the user's words — why it's off>"
- strike: <1 | 2>
- reconciliation: <blank until repaint; then what changed>
```

The next run reads this file and must account for **every OPEN entry**, flipping each to
`RESOLVED` (corrected/narrowed, with what changed) or `DROPPED`. **2-strike rule:** a claim
(or the same *kind* of overreach) disputed a second time is **DROPPED**, not just softened,
and its generating pattern is added to the **Distrusted patterns** rollup at the bottom of
`disputed.md` so future synthesis stops producing it without ✓VERIFIED quote-level evidence.
This closes the anti-Barnum loop: claims aren't just *falsifiable in principle*, they get
*actually falsified in practice* and the portrait corrects.

---

## Step 6 — Archive, confirm, gauge

**Archive before mutating (do this before the Step-4A overwrite, in practice — listed here for
completeness):** before overwriting `PORTRAIT.md`, copy the existing one to
`portrait/_ARCHIVE/PORTRAIT_<prior-date>.md`. The frozen snapshots are already immutable, so they
need no archiving — but the *current* file gets overwritten, so its prior state must survive.
(Per `CLAUDE.md` — "archive before mutating," even when you're confident.)

Confirm:

```
portrait: minted _PORTRAIT_<NNN+1> (frozen) + refreshed PORTRAIT.md
  prev: _PORTRAIT_<NNN>
  sources: <N chat / M writing / K work, stratified <range>> + <J handoffs, calibration, P rules>
  claims: <total> (✓VERIFIED <x> / ?INFERRED <y>)   ← if ?INFERRED dominates, say so: the portrait is still thin
  delta:
    • <bullet 1>
    • <bullet 2>
  disputes: <open count from identity/disputed.md, addressed this pass>
```

Then emit the end-of-turn bottom line (and the context gauge — a full corpus synthesis is an
Opus / ultra job and lands at medium/heavy context, so the gauge fires; recommend a reboot if heavy).

---

## What /portrait never does

- **Never builds a mask.** No clone, agent, persona, or voice-imitator. The audience is the user, only.
- **Never makes an uncited claim.** No evidence → the claim is deleted, not softened. No Barnum lines.
- **Never edits or deletes a frozen snapshot.** The snapshot number is the version control.
- **Never lets corpus or portrait content leave the machine.** No upload, no external API, no telemetry.
  Sharing is a separate manual act through the release gate — never automatic. (The optional recall
  index `identity/recall.db` follows the same rule: local-only, gitignored, embeddings computed locally.)
- **Never requires recall.** The semantic layer is opt-in and fail-soft — absent or broken, the run
  uses grep exactly as today. A recall hit never bypasses the citation discipline.
- **Never writes personal content into a `*.template.md` file.** Templates ship; live files are
  `.gitignored`. If the fence doesn't cover a new live artifact, fix the fence first.
- **Never overwrites `PORTRAIT.md` without archiving the prior version first.**
- **Never resolves a real tension artificially** to make the portrait tidier or more flattering.
- **Doesn't touch the core loop** — boot, handoff, `_NEXT`, audit, memory. Portrait reads the
  decision-history; it never writes to it.

---

## The anti-Barnum guarantees this method encodes

These are the structural commitments that separate Portrait from the horoscope genre. They are
not advisory — they are the discipline the steps above enforce:

1. **Every claim cites its evidence.** Quote/paraphrase + named source (file / `_NEXT_NNN` /
   date-slice). No citation → no claim.
2. **Every claim is marked for verification.** `✓VERIFIED` (multiple corroborating sources) vs.
   `?INFERRED` (single/weak), with an honest `high|medium|low` confidence.
3. **Every claim is falsifiable.** Each carries a `falsifier:` — the observation that would prove
   it wrong. A claim that nothing could disconfirm is a Barnum line and is banned.
4. **Every claim is disputable in practice, not just in principle.** The dispute channel
   (`identity/disputed.md`) logs the user's objections and the next run must address each one —
   remove, downgrade, or re-ground.
5. **The Barnum test is run on every line.** "Would this be true of most thoughtful people?" →
   if yes, delete or sharpen. Vague flattery and universal-trait-as-personal are explicitly banned.
6. **Coverage is stated honestly.** The portrait reports what corpus was actually sampled and how;
   it never claims coverage it doesn't have, and over-uses `?INFERRED` rather than over-claiming.
7. **Tensions are kept, not flattened.** Real contradictions (including say/do gaps surfaced by the
   decision-history) are named and held, not resolved into a comfortable both-and.
8. **The arc is auditable.** Frozen dated snapshots + the explicit delta make the becoming-arc a
   diff anyone can check — not a black-box profile that silently evolves (the incumbent's failure
   this method exists to invert).
