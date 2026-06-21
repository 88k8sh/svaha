# sources — corpus manifest (TEMPLATE)

> **TEMPLATE. Zero personal content — PLACEHOLDER PATHS ONLY.**
> Go live: `cp sources.template.md sources.md`, then point the entries at your real
> local paths. Live `sources.md` is gitignored (it contains real paths); this
> template stays tracked. (Scheme: `../.gitignore`.)
>
> **What this is:** the auditable, reproducible list of every corpus that feeds the
> portrait. Each entry gets a stable `<source-id>` — the same id that every claim in
> `PORTRAIT.md` cites in its `ev:` line. If a claim cites a `<source-id>` that isn't
> here, that claim is unanchored and `/mirror` refuses to show it.
>
> **Local-first (HARD):** these are paths on THIS machine. The corpus never
> auto-leaves. This manifest exists so the portrait is reproducible and auditable,
> not so the data travels.

---

manifest rev: <YYYY-MM-DD or hash>
machine: <hostname — local only>

## Source-id format
`<KIND>-<NN>` — KIND ∈ {CHAT, WRITE, WORK, LOOP}. Stable forever; claims cite these.

---

## A. Imported corpus (chat exports + writings + work)
*The "your own already-existing multi-source corpus" wedge — not in-app entries.*

### CHAT-01 — <name of chat export, e.g. assistant conversation export>
- path: <ABSOLUTE local path, placeholder — e.g. /Users/<you>/exports/chat.json>
- span: <date range covered>
- format: <json | md | txt>
- count: <# conversations / messages>
- notes: <what kind of material; any redactions applied>

### WRITE-01 — <personal writings / essays / journals>
- path: <ABSOLUTE local path, placeholder>
- span: <date range>
- format: <md | docx | txt>
- notes: <placeholder>

### WORK-01 — <work artifacts that reveal how you think>
- path: <ABSOLUTE local path, placeholder>
- span: <date range>
- notes: <placeholder>

## B. Throughline-loop corpus  ← the structurally-unique source
*How you actually operate, recorded by the loop itself. This is the source class
chat/journaling tools structurally lack — it's why §4 Operator-patterns exists.*

### LOOP-01 — frozen handoffs
- path: <ABSOLUTE path to next/ — placeholder, e.g. /Users/<you>/.../next/>
- content: every `_NEXT_NNN.md` — decisions made, with conviction tags + outcomes
- feeds: §4 operator-patterns (conviction-vs-outcome calibration)

### LOOP-02 — calibration / ledger
- path: <ABSOLUTE path to 30_LEDGER/ — placeholder>
- content: conviction misses, corrections promoted to rules at 2nd occurrence
- feeds: §4 operator-patterns (which corrections recur)

### LOOP-03 — promoted rules
- path: <ABSOLUTE path to CLAUDE.md — placeholder>
- content: the rules that corrections hardened into — your operating constraints
- feeds: §4 operator-patterns (stable identity as an operator)

---

## Coverage / gaps (auditability)
- corpus spans: <earliest> → <latest>
- known blind spots: <periods or domains with no source — placeholder>
- excluded by choice: <anything deliberately kept out, e.g. raw vault T2 — placeholder>
