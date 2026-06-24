# Session Fixes — Bug Log

Append-only. Bugs caught and corrected during sessions. One entry per fix.
Written by `/reflect` (via `/handoff` step 4). Do not edit existing entries.

---

## Format

```
## YYYY-MM-DD — [one-line description]
- **Bug:** [what was wrong]
- **Fix:** [what was changed and where]
```

---

## 2026-06-24 — Install one-liner substituted the wrong placeholder → silently unwired hooks
- **Bug:** `docs/start.html` Step 4's manual `sed` pipeline substituted `<system-dir>` when, post kit-dir/system-dir split, every path placeholder in `settings.json.snippet` is `<kit-dir>` (the lone `<system-dir>` is a comment, stripped before substitution). It produced *structurally-valid* JSON — so it printed "OK — settings.json written and valid" — while leaving every hook command path a literal `<kit-dir>`, so no guard hook ever fired. A green checkmark over a fully-unwired system. The docs drifted from the snippet at the split; SYNC_MAP row 51 still named the old `INSTALL.html` location.
- **Fix:** Removed the manual pipeline as a step — `setup.sh` (which substitutes `<kit-dir>` correctly and safe-merges existing configs) now owns `settings.json` end-to-end, with its fresh-write prompt flipped `[y/N]`→`[Y/n]` so `return` wires it. The manual path is demoted to a collapsed fallback with the token corrected to `<kit-dir>`→`$(pwd)`. Verify step → `bash bin/doctor.sh` (it catches a leftover `<kit-dir>`). SYNC_MAP row 51 repointed to `docs/start.html` with a token-drift warning. Verified: corrected fallback emits valid JSON, 0 leftover placeholders.
