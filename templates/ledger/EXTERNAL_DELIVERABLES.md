# EXTERNAL_DELIVERABLES — out-of-tree supersession registry

> **Append-only.** The missing completion signal for deliverables that live
> OUTSIDE this tree (a shipped package, an essay, a sibling repo — anything not
> under this `<system-dir>` root). They write no `(_NEXT_NNN)` CHANGELOG marker,
> no `.consumed` sidecar, and no commit here — so a finished out-of-tree move
> leaves its `_NEXT` slot reading live and can re-mint into a fresh slot that
> defeats every staleness gate. The COMPLETING session records the supersession
> here via `bin/external-done.sh`; `boot.md` reads it FIRST on every boot.
> **Never edit a line — only append.**

> **When to write a row:** you finished a `_NEXT` move whose result lives outside
> `<system-dir>` (a published package, a doc in a sibling repo) so it left no
> in-tree completion signal. Record it (append-only, idempotent):
>
> ```
> <kit-dir>/bin/external-done.sh <system-dir> <predecessor> "<superseder>" "<note: slot + provenance>"
> ```
>
> *Illustrative only (not live rows): `my-context-kit-v1` → `acme-context plugin`
> (`_NEXT_007 m2`; shipped to a sibling repo, source archived); `architecture-essay
> draft` → `essay published elsewhere` (`_NEXT_012 m1`; completion never wrote back
> in-tree). Real rows are appended below the table by the script.*

| recorded (UTC) | predecessor → superseder | note (slot + provenance) |
|---|---|---|
