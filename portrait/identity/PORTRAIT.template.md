# PORTRAIT — current synthesis (TEMPLATE)

> **This is a TEMPLATE. Zero personal content — placeholders only.**
> Go live: `cp PORTRAIT.template.md PORTRAIT.md`, then fill. The live `PORTRAIT.md`
> is gitignored; this template stays tracked. (See `../.gitignore` for the scheme.)
>
> **What this is:** the *current* synthesized portrait — the living "who you are
> now" file, derived from the frozen snapshots in `portraits/`. It is the
> numbered-snapshot pattern's "current synthesis" half: `portraits/_PORTRAIT_NNN.md`
> are the frozen dated snapshots; **this** file is the rolled-up current read.
> The **becoming-arc is the diff across snapshots**, not anything stated here.
>
> **How it's built:** `/portrait` synthesizes this from the corpus listed
> in `sources.md`, reconciles every OPEN dispute in `disputed.md`, freezes a new
> `portraits/_PORTRAIT_NNN.md`, and rewrites this file.
>
> **The rule that makes this not-a-horoscope:** every claim below MUST carry an
> evidence citation + marker + confidence. A claim with no resolvable evidence is
> a bug — drop it or anchor it. `/mirror` will refuse to show unanchored claims.

---

meta:
- synthesized: <YYYY-MM-DD>
- from snapshot: portraits/_PORTRAIT_<NNN>.md
- corpus manifest: sources.md (rev <hash-or-date>)
- open disputes carried in: <count>   ← must be 0 after a clean repaint

**Claim format (every bullet below uses this):**
```
- <claim, one sentence>  [✓VERIFIED|?INFERRED|✗UNCERTAIN] (confidence: high|medium|low)
  ev: <source-id> → "<quote or locator>"   [; <source-id> → "..." for multi-source]
```

---

## 1. Stable identity
*Who you are across time — the parts the corpus shows holding steady. High bar: prefer ✓VERIFIED, quote-anchored.*

- <stable trait / value / commitment — placeholder>  [✓VERIFIED] (confidence: high)
  ev: <source-id> → "<direct quote from corpus>"; <source-id> → "<second corroborating quote>"
- <another stable trait — placeholder>  [?INFERRED] (confidence: medium)
  ev: <source-id> → "<pattern locator: e.g. recurs across 6 entries 2024–2026>"

## 2. Becoming / growth themes
*The arc — what's actively shifting. State the FROM → TO and cite the snapshot diff that shows the movement, not just the endpoint.*

- <theme>: shifting from <prior stance> → <current stance>  [?INFERRED] (confidence: medium)
  ev: _PORTRAIT_<NNN-earlier>.md "<old claim>" vs _PORTRAIT_<NNN-later>.md "<new claim>"; <source-id> → "<corpus quote marking the turn>"
- <theme>: <placeholder>  [?INFERRED] (confidence: low)
  ev: <source-id> → "<locator>"   ← low confidence: arc is one data point, watch next snapshot

## 3. Unresolved tensions
*Genuine contradictions the corpus shows you holding — not flaws to resolve, just the live forks. These are often the truest part; don't smooth them.*

- <tension: X pulls against Y>  [✓VERIFIED] (confidence: high)
  ev: <source-id> → "<quote showing side X>"; <source-id> → "<quote showing side Y>"
- <tension — placeholder>  [?INFERRED] (confidence: medium)
  ev: <source-id> → "<locator>"

## 4. Operator-patterns  ← the structurally-unique section
*How you actually OPERATE over time — drawn from the Svaha loop's own record, which chat/journaling tools structurally lack. Sources: the frozen `_NEXT` handoffs, the conviction-vs-outcome calibration history, and corrections that got promoted to rules. This is the part no competitor can copy without a context-OS.*

- <pattern in how you decide / hand off / calibrate>  [✓VERIFIED] (confidence: high)
  ev: next/_NEXT_<NNN>.md → "<conviction:high … outcome:FAILED — a calibration miss>"; CLAUDE.md → "<the rule that miss promoted>"
- <pattern: where conviction and outcome diverge>  [?INFERRED] (confidence: medium)
  ev: <N handoffs where high-conviction calls held vs failed — locator>
- <pattern: which corrections recur>  [✓VERIFIED] (confidence: high)
  ev: 30_LEDGER/<ledger file> → "<the correction, promoted at 2nd occurrence>"

---

## Provenance footer (auditable)
- every claim above resolves to a `<source-id>` in `sources.md`: <yes/no — must be yes>
- claims dropped this repaint (disputed/unanchored): <list or none>
- next repaint should re-examine: <weak spots, low-confidence arcs, stale citations>
