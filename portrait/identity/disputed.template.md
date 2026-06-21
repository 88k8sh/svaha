# disputed — anti-Barnum feedback log (TEMPLATE)

> **TEMPLATE. Zero personal content — placeholders only.**
> Go live: `cp disputed.template.md disputed.md`, then log real disputes here.
> Live `disputed.md` is gitignored; this template stays tracked. (Scheme: `../.gitignore`.)
>
> **What this is:** the falsifiability ledger. Every claim the user marked **wrong**,
> **overreaching**, or **outdated** lands here so the next synthesis corrects it.
> This is the mechanism that kills the horoscope/Forer problem: a portrait you can't
> dispute is a fortune cookie. A disputable, dispute-tracked portrait is not.
>
> **Append-only.** This is a running log (CLAUDE.md: append-only logs ≠ numbered
> snapshots). Never delete a resolved entry — the dispute history is itself signal
> about which inference patterns to distrust.
>
> **The 2-strike rule (mirrors the calibration loop):** a claim disputed ONCE is
> corrected/narrowed at the next repaint and marked RESOLVED. A claim (or the same
> *kind* of overreach) disputed a SECOND time is **dropped entirely**, and the
> generating pattern is flagged DISTRUST so future synthesis stops producing it.
>
> **How entries arrive:** `/mirror dispute "<claim>"` appends an OPEN entry here.
> `/portrait` must reconcile every OPEN entry and flip it to RESOLVED/DROPPED.

---

## Status legend
- **OPEN** — logged, not yet reconciled. The next repaint MUST address it.
- **RESOLVED** — the portrait was corrected/narrowed; says what changed.
- **DROPPED** — 2nd strike; claim removed and its pattern marked DISTRUST.

---

## Disputes

### D-001  (OPEN)  — <YYYY-MM-DD>
- claim disputed: "<the exact claim text the user pushed back on>"
- shown in: PORTRAIT.md §<section> / snapshot _PORTRAIT_<NNN>
- reason: <wrong | overreaching | outdated>
- user note: "<one line in the user's words — why it's off>"
- strike: 1
- reconciliation: <blank until repaint; then: corrected to "<new claim>" / narrowed / dropped>

### D-002  (RESOLVED)  — example shape, replace
- claim disputed: "<old claim>"
- shown in: snapshot _PORTRAIT_<NNN>
- reason: overreaching
- user note: "<...>"
- strike: 1
- reconciliation: narrowed to "<tighter claim with confidence lowered to low>" in _PORTRAIT_<NNN+1>; evidence re-cited to <source-id>.

### D-003  (DROPPED)  — example shape, replace
- claim disputed: "<claim>"
- shown in: snapshot _PORTRAIT_<NNN>
- reason: wrong (2nd strike — same overreach as D-00X)
- user note: "<...>"
- strike: 2
- reconciliation: claim removed; generating pattern "<pattern name>" marked **DISTRUST** — future synthesis must not infer this class of claim without ✓VERIFIED quote-level evidence.

---

## Distrusted patterns (rollup — read before each repaint)
*Patterns that hit 2 strikes. Synthesis must not reproduce these without direct quote evidence.*
- <none yet — populate as DROPPED entries accumulate>
