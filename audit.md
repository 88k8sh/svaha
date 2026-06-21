# /audit — System Audit

Execute immediately, no preamble. Do not ask for confirmation.

Optional arg: `/audit 1` or `/audit 2` forces a specific tier. No arg = auto-select by density.

---

## Step 1 — Read audit state + count delta

1. Read `<system-dir>/30_LEDGER/audit-state.md` — get `last_audit_next` and `last_audit_date`.
2. Count all `_NEXT_NNN.md` files in `<system-dir>/next/` — find the highest number currently existing.
3. Compute `delta = highest_current - last_audit_next`.
4. Select tier:
   - Forced arg → use that tier
   - `delta == 0` or `last_audit_date == never` → **Tier 2** (first run or no sessions since last audit)
   - `delta >= 15` → **Tier 2**
   - `delta >= 5` → **Tier 1**
   - `delta < 5` → emit `audit: delta is N — too soon (threshold: 5). Run /audit 1 or /audit 2 to force.` and stop.

Announce: `audit: Tier N — delta N files since last audit (last: _NEXT_NNN, current: _NEXT_NNN)`

---

## Tier 1 — Lightweight drift check (Sonnet)

Read these files (parallel):
- `<system-dir>/memory/MEMORY.md` — the index
- `~/.claude/settings.json` — deny/allow rules
- `<system-dir>/_LOADUP.md` §2 (settled facts)
- `<system-dir>/_NEXT.md` (the _NEXT spec / handoff rules)
- The delta `_NEXT` files (all files with number > `last_audit_next`) — read their **Push to _LOADUP** sections only

Check for:
1. **Unpushed facts** — anything in a delta _NEXT's "Push to _LOADUP" section that isn't in _LOADUP §2 yet
2. **Stale memory entries** — MEMORY.md pointers to files/paths that may have moved (flag, don't auto-fix)
3. **Settings drift** — deny rules referencing paths that no longer match the system structure
4. **Rule violations / smells** — *Hard violation:* a delta _NEXT with content edited after creation (frozen-file breach; check git blame if repo). *Soft smell (flag for review, NOT a violation):* a delta _NEXT >30 lines — the under-30 target is a `handoff.md` convention, not an enforced cap; exceeding it usually means content belonging in CHANGELOG / USER_TASKS / _LOADUP leaked into the handoff. Nothing breaks — it's a routing nudge. Note the file size; don't flag it as a breach.
5. **`_NEXT` consumed-sidecar reconcile** — run `<system-dir>/bin/next-live.sh <system-dir> --check`. Exit 0 = clean. Exit 1 prints the desyncs: `DONE-UNCONSUMED` (a `_NEXT` whose moves are finished but was never stamped `.consumed` — it lingers in the live list) and `ORPHAN` (a `.consumed` with no `_NEXT_NNN.md`). Report verbatim; the fix for DONE-UNCONSUMED is `touch next/_NEXT_NNN.consumed`. Cheap deterministic check — the script is the single source of truth for the live set (concurrent sessions mutate `next/`, so never hand-count it).

Output format:
```
── Tier 1 Audit ─────────────────────────────
unpushed facts (N):
  • [_NEXT_NNN] "<fact>" → push to _LOADUP §2
stale memory (N):
  • [memory-file] "<entry>" — verify path still valid
settings drift (N):
  • <finding>
rule violations (N):
  • <finding>
_NEXT consumed-sidecar reconcile:
  • <next-live.sh --check output, or "clean">
clean: <list anything that checked out fine>
─────────────────────────────────────────────
```

If nothing found in a category: `clean` for that line. If all clean: `all clear — no drift found`.

---

## Tier 2 — Full coherence audit (Opus)

Do everything in Tier 1, then additionally:

Read (parallel):
- All delta `_NEXT` files in full (not just Push to _LOADUP)
- `<system-dir>/30_LEDGER/CHANGELOG.md` — entries since `last_audit_date`
- `<system-dir>/_LOADUP.md` in full
- `<system-dir>/SYNC_MAP.md` — the file-dependency coupling map (for the sync-map coherence check below)

Check for:
1. **Everything in Tier 1**
2. **Contradiction scan** — do any delta _NEXT "settled facts" contradict _LOADUP §2? Flag both sides.
3. **Carry-forward debt & silent dropouts** — two failure modes: **(a) debt** — a move recurring across 3+ _NEXT files without progress (stuck; flag to kill or schedule); **(b) dropout** — a *live* move that appeared, then vanished from later _NEXT files with no CHANGELOG completion and no USER_TASKS promotion (it slipped silently — the worse case). Match on move *intent*, not exact text (a reworded move evades string matching). Handoff catches dropouts at wrap (CLAUDE.md "Surface what's slipping" + handoff.md continuity check); /audit is the backstop — flag any dropout that wrapped without being named, and any "standing since _NEXT_NNN" claim whose intervening files don't actually contain the move.
4. **_NEXT number inflation rate** — compute sessions per week since last audit. If >3/week: note it (signals high churn, possibly too many short sessions).
5. **Missing CHANGELOG entries** — CHANGELOG should have an entry for any structural change mentioned in delta _NEXT files. Flag gaps.
6. **Sync-map coherence** — for each structural change in the delta (renamed path, schema/format/count change, new/removed command or script), confirm `SYNC_MAP.md` still describes it correctly and its named targets were all updated. Spot-check 2–3 high-blast-radius couplings (the boot fast-path lists agree; every `§N` pointer resolves; any count referenced in multiple docs matches across them). Flag any coupling the map misses or mis-states. Confirm any slash command added since the last audit appears in SYNC_MAP §3.
7. **Guard health review** — two essentials, plus a spot-check:
   - **Hook registration:** read `~/.claude/settings.json` and verify each Core hook is wired *and* its script exists on disk — PreToolUse `security-guard.py` + `version-guard.py` + `drift-guard.py`; PostToolUse `context-canary.sh`; Stop `launchpad-nudge.sh` + `memory-reflect.sh` + `resume-line-guard.sh` + `coherence-check.py --stop`; SessionEnd/PreCompact `session-end-backstop.sh`; SessionStart `session-start-marker.sh`. Flag any `missing hook: <name> — not in settings.json` or `broken hook: <name> — registered but script not found`.
   - **Over-fires (tighten):** from `<system-dir>/30_LEDGER/drift-guard-overfires.md`, count open `**Refinement hint:**` entries per label, excluding any block marked "Counter reset"/"(resolved)". Any label with **3+ open over-fires** and no catch in between → trigger too broad; recommend the tightening its hints name. Below threshold, note the running open count.
   - **Also spot-check:** any slash command added since the last audit is registered in all three of `coherence-check.py` `REGISTERED_COMMANDS` + `settings.json` (if it has a hook) + `_LOADUP §2` (`unwired: <cmd> missing from <where>`); and any `drift-guard.py` coupling label with no corresponding verdict block in `drift-guard-evidence.md` is a candidate to retire (human call, never auto-remove).
8. **Semantic coherence (knowledge-base health)** — a **flag-for-review pass only, never auto-fix** (same posture as the rest of /audit). Read across the ledger, `_LOADUP.md`, `CLAUDE.md`, and the delta `_NEXT` files for *meaning*-level rot the structural checks can't see, flagging four types with their locations: **contradictions** (any two of the doc families assert conflicting facts — wider than check #2's _NEXT-vs-_LOADUP scan), **orphans** (a reference in `_LOADUP §3`/the maps pointing at a missing file, OR a real artifact nothing points to), **parallel implementations** (two scripts/commands/hooks doing the same job — callers split, one silently diverges), and **staleness** (a `[[wikilink]]`/`§N`/`see X` pointer aimed at a moved or renumbered target). Spot-check high-traffic pointers rather than crawling every link; surface everything for human judgement.

Output format:
```
── Tier 2 Audit ─────────────────────────────
[all Tier 1 findings]

contradictions (N):
  • _LOADUP says "<X>" but _NEXT_NNN says "<Y>"
carry-forward debt (N):
  • "<move>" stalled N sessions — decide: kill or schedule
inflation rate: N sessions/week [normal | elevated | high]
missing changelog (N):
  • <structural change> in _NEXT_NNN — no CHANGELOG entry
sync-map coherence:
  • <finding or "current">
guard health:
  hooks: <all present | missing: X | broken: Y>
  over-fires (open): <label> ×K open  [or "none open"]
  spot-check: <unwired commands / retire-candidate labels, or "clean">
semantic coherence (flag-for-review):
  contradictions (N): • <doc A> says "<X>" but <doc B> says "<Y>"
  orphans (N): • <ref> in <map/§3> → missing on disk  /  • <artifact> present but unreferenced
  parallel impls (N): • <A> and <B> both <job> → pick canonical, retire the other
  staleness (N): • <link/§N pointer> in <file> → no longer resolves
─────────────────────────────────────────────
```

---

## Step 3 — Recommended actions

After the findings block, emit a short ordered action list:
```
recommended actions:
  1. [push] Push "<fact>" to _LOADUP §2  ← always first if any unpushed facts
  2. [decide] Kill or schedule stale move: "<move>"
  3. [fix] <other finding>
  ...
```

Maximum 5 actions. If more than 5 findings, prioritize: unpushed facts → contradictions → carry-forward debt → everything else.

---

## Step 4 — Update audit state

Write back to `<system-dir>/30_LEDGER/audit-state.md`:
```
last_audit_next: <current highest number>
last_audit_date: <today's date YYYY-MM-DD>
last_audit_tier: <1 or 2>
```

Confirm: `audit state updated → next Tier 1 at _NEXT_NNN+5, Tier 2 at _NEXT_NNN+15`

---

## What /audit never does

- Never edits _NEXT files (they are frozen)
- Never pushes facts to _LOADUP automatically — always surfaces them for human action
- Never deletes or archives files
