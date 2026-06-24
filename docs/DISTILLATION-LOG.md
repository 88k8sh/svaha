# Distillation Log — Throughline → Throughline Core

How the Core was distilled from the full kit. Every CUT and SLIM below carries a one-line,
charter-justified why. KEEP components (copied verbatim) are listed last for completeness.

Charter reference: legibility budget (§2 — afternoon-readable, deletion-first, concise-not-minimal),
hard invariants (§1), trust tiers (§5 — core vs. opt-in bolt-on).

---

## CUT (not shipped in Core)

| Component | Why (charter-justified) |
|---|---|
| `bin/context-pct.sh` | The measured-% statusLine bridge the charter names by name as a prime cut. It's a precision upgrade over byte-size (input-token-based, known accuracy limits), not a safety/continuity requirement; the canary's byte-size fallback covers context-fill warning with zero dependency. Removing it drops a jq/Claude-Code-version coupling across 4 files. |
| `hooks/premortem-suggest.sh` | The only judgment-layer (not safety/continuity) hook; advisory-only, re-raises a rule already in `CLAUDE.md`'s Operator-layer Premortem section. Charter §4 "the Nth hook" tripwire: a hook whose sole effect is re-emitting an existing instruction guards nothing — shrinking the always-on hook surface costs no safety. |
| `docs/index.html` | 107KB marketing landing page; pure promotion, ~108KB of unvettable-by-skim HTML/JS, contributes nothing to the runnable Core. Belongs on a published-site branch, not the kit a user reads and trusts (charter §2). |
| `docs/compare.html` | 45KB competitor-comparison marketing page; positioning, not Core. Its honest substance already lives in `CREDITS.md` and `portrait/README.md`. |

---

## SLIM (shipped, accretion/duplication removed; every guard + continuity step kept verbatim)

| Component | What was trimmed | Why |
|---|---|---|
| `CLAUDE.md` | Collapsed the measured-% gauge threshold to byte-size only; deduped the Operator-layer "safety skeleton + judgment layer" framing (kept one statement); compressed the ~24-session-dropout and dashboard-degradation incident parentheticals (date/artifact kept); tightened the self-interrogation/proportionality prose. Every HARD RULE (6), the Risk Gate + always-stop list + auto-escalation overrides, the dormant auto-exec safety statement, fix→diagnose→prevent, and all file-mutation/secret guards kept verbatim. | It's the always-loaded surface — permanent context budget. Deletion-first (§2). Modest byte reduction because the file is overwhelmingly load-bearing; fidelity wins over a cosmetic line-count target (charter §2 "concise, not minimal"). |
| `boot.md` | Compressed RESUME-WITH-VERIFICATION steps A–D to procedure-only (moved the "why" to `_NEXT.md`); dropped duplicated failure-mode narration. All four steps + the exact Output block + opener/file-mismatch guard kept verbatim. | The resume entry point; keep the contract, cut the prose that `_NEXT.md`/`session.md` already carry. |
| `handoff.md` | Collapsed the triple explanation of the Verified-Handoff header fields into one quick-reference pointing at `_NEXT.md` as canonical; deleted the "Verdict + strategy memory" restatement. Warrant gate, Continuity check, cold-reader bar, consumed-stamp, read-back, File invariant kept verbatim. Plus: made `git push` a knowing opt-in (security finding). | Heaviest file in the area; the field semantics were explained 3× here + once in `_NEXT.md`. Single-source-of-truth (charter §2 duplication). |
| `audit.md` | Tier-2 check #7 (guard health) collapsed to two essentials (hook-registration + over-fire tally) + a one-line spot-check; check #8 (semantic coherence) collapsed from four fully-specified sweeps to one paragraph naming the four rot types. Removed the jsonl-dependent Tier-1 guard-fire tally + dead-guardrail/logging-gap sub-checks (their data source was cut). Tier selection, Step-4 state write-back, "what /audit never does" kept. | Second-biggest accretion offender; the audit-of-the-audit pushed the kit past afternoon-readable (charter §2). Also a dangling-ref fix (see below). |
| `SYNC_MAP.md` | Deleted the context-gauge measured-% coupling row (collapsed to byte-only); removed `premortem-suggest`/`UserPromptSubmit` from the hook row; dropped the "(if you keep one)" / "(if your kit uses it)" hedges for files the Core actually ships. †proven-by-incident markers kept. | Always-referenced coherence map; state couplings as fact for shipped files, drop the bolt-on row (charter §2). Also a dangling-ref fix. |
| `README.md` | Cut the Live-site banner + `compare.html` link; merged "What you get" into "The loop"; compressed "Composes with your stack" to 3 lines pointing at CREDITS; reduced the context-% bullet to one byte-size sentence; dropped `context-pct.sh` from the Layer-3 table. Install + five-layer table + Privacy paragraph kept. | Front door; remove marketing accretion (charter §2). Also a dangling-ref fix. |
| `CREDITS.md` | Compressed the 22-item "Ideas folded in" catalog to one sentence naming the 5 most load-bearing borrowed patterns; one-lined "Related projects" into the integration-bet closer. The 5 named upstreams + reuses-no-code framing kept. | The honest provenance is load-bearing; the 22-row catalog read as positioning, not Core (charter §2). |
| `setup.sh` | Steps 5–6 (Context7 + Superpowers interactive installs) collapsed into one print-only "Optional companions" block; removed the inline `claude mcp add` execution and the API-key read. Steps 1–4 + the start step kept verbatim. | Removed the only place setup.sh executed a third-party install and read a key — shrinks both the read length and the security surface (charter §1.3 network/§4 "feature whose code you can't fully explain"). |
| `portrait/README.md` | Cut the 8-row competitor scorecard table + its per-axis "what the table shows" analysis down to the 2-sentence honest claim it already states (evidence-anchoring + decision-history are the only real edges). Method (recall.py, templates, privacy fence) untouched. | The scorecard is marketing, not how-to; the bolt-on's internal docs were ~half prose a Core reader would wade through (charter §2/§5). |
| `bin/drift-guard.py` | Dropped the `record()` machine-log subsystem + `drift-guard-fires.jsonl` writes + `DRIFT_GUARD_NO_LOG` handling; compressed the docstring essays. All coupling rows, the diff-gate, WORKSPACE_ROOTS scoping, and fail-open exits unchanged (firing behavior smoke-tested identical). 215→174 lines. | The fires.jsonl log was audit instrumentation, not the prevent layer's job (charter §2 "nothing that doesn't earn its place"). |
| `bin/coherence-check.py` | Removed the `--stop` pre-logging detector (`get_session_start`/`parse_recent_changelog_claims`/`resolve_claim_path`) — ~90 lines of the file's hardest-to-vet fuzzy logic for the narrowest catch. Kept `boot()` in full + plumbing-newer-than-CHANGELOG + audit-delta nudge. 291→200 lines. | "Clever-but-hard-to-fully-explain" logic the legibility budget warns against (charter §4 "a feature whose code you can't fully explain"). |
| `hooks/context-canary.sh` | Cut the PRIMARY measured-% block + pctfile freshness/parse logic; byte-size (400KB/700KB) is the sole trigger. Throttle + yellow/red sentinels kept. 93→47 lines. | Removes the `context-pct.sh` coupling; the byte path delivered the original value (charter §2). |
| `hooks/launchpad-nudge.sh` | Cut the measured-% primary block (the parser triplicated across 3 files); byte-size (1.2MB) + once-per-session sentinel kept. 64→30 lines. | Removes the copy-pasted % parser; same single-heavy-session nudge (charter §2 duplication). |

---

## Dangling references fixed (kept file → cut component)

- `CLAUDE.md` completeness spec Layer-3 listed `context-pct.sh` + `premortem-suggest.sh` → removed.
- `CLAUDE.md` context-gauge thresholds referenced the measured-% bridge → rewritten byte-size only.
- `SYNC_MAP.md` had a measured-% coupling row + `premortem-suggest`/`UserPromptSubmit` in the hook row → removed/collapsed.
- `README.md` linked `docs/compare.html`, the Live-site banner, and listed `context-pct.sh` → removed.
- `settings.json.snippet` wired `statusLine`→`context-pct.sh` and `UserPromptSubmit`→`premortem-suggest.sh` → both blocks removed (JSON re-validated).
- `audit.md` Tier-1 guard-fire tally + Tier-2 dead-guardrail/logging-gap sub-checks read `drift-guard-fires.jsonl` (no longer written) → removed; hook-registration list updated to the actual kept hook set.
- `bin/drift-guard.py` wrote `drift-guard-fires.jsonl` → writer removed.
- `.gitignore` ignored `drift-guard-fires.jsonl` (no longer produced) → line removed.
- `30_LEDGER/CHANGELOG.md` described building the cut files (origin-system history) → reset to a clean Core-distillation seed entry (kept format block + append-only header).

---

## KEEP (copied verbatim, no change)

`session.md`, `reflect.md`, `foldin.md`, `_NEXT.md`, `_LOADUP.md`, `SYSTEM_MAP.md`, `AGENTS.md`,
`bin/next-write.sh`, `bin/next-live.sh`, `bin/security-guard.py`, `bin/version-guard.py`,
`hooks/memory-reflect.sh`, `hooks/resume-line-guard.sh`, `hooks/session-end-backstop.sh`,
`hooks/session-start-marker.sh`, `.claude-plugin/plugin.json`, `LICENSE`, `docs/essay.md`,
`memory/MEMORY.md` + `memory/README.md`, the `30_LEDGER/` scaffolds (except CHANGELOG, reset),
`_ARCHIVE/README.md`, `next/_NEXT_001.md`, and the `portrait/` functional method (recall.py,
templates, mirror.md, recall.md, the `.gitignore` privacy fence).

---

## Self-check (run at build close)
- Every `.sh` passes `bash -n` (9 scripts). ✓
- Every `.py` passes `python3 -m py_compile` (5 scripts). ✓
- `settings.json.snippet` parses as JSON with comments stripped. ✓
- `drift-guard.py` firing behavior smoke-tested identical after `record()` removal (structural fire, diff-gate suppression, frozen-handoff, boot-loop). ✓
- No surviving references to any cut component outside the CHANGELOG distillation note. ✓
