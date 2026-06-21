# Drift Guard Evidence — Running Log

Append-only. Records instances where the drift-guard hook caught real drift (i.e. a structural edit that did require a follow-up coupling update). Evidence that the prevention layer is earning its cost.

Also records notable false positives with explanation — so patterns of noise can be diagnosed and the guard refined.

---

## Format

```
### YYYY-MM-DD — [one-line description]

**Guard fired on:** [file edited]
**What happened:** [what the coupling check caught, or why it was a false positive]
**Action taken:** [what was updated, or "false positive — no action"]
```
