# /init — Scaffold a fresh project's data layer

Execute immediately, no preamble. `/init` turns the **current directory** into a Svaha `<system-dir>` — the per-project data root the loop boots from. Run it once, in a new project that already has the kit installed (`setup.sh` has run) but no handoff data yet.

It scaffolds **only data** — the per-project half of the five-layer completeness spec. The machinery (slash commands, hooks, `bin/`) already lives in `<kit-dir>`, installed globally; `/init` never copies it. That separation *is* the kit-dir/system-dir split: machinery baked once, data per-project.

## When to run

- A fresh project where boot / `/session` / **svaha** reports *"the project isn't initialized — run `/init`"* (the bounded search around CWD found no `_LOADUP.md`).
- **Not** to re-scaffold an initialized project: if CWD already holds a `_LOADUP.md`, `/init` refuses — it would clobber your filled-in data. Use `/session` instead.

## Step 1 — guard + scaffold (one block, run from the project root)

CWD becomes `<system-dir>`. `<kit-dir>` is already baked to an absolute path in this installed command, so the template copies resolve. Run:

```bash
set -u
KIT="<kit-dir>"
DEST="$(pwd)"

# Guard — never clobber an initialized project.
if [ -f "$DEST/_LOADUP.md" ]; then
  echo "ALREADY-INIT: $DEST/_LOADUP.md exists — /init refuses to clobber. Run /session instead."
  exit 0
fi

mkdir -p "$DEST/next" "$DEST/ledger" "$DEST/memory" "$DEST/_ARCHIVE"

# Layer 1 — handoff loop (data half)
cp "$KIT/_LOADUP.md"        "$DEST/_LOADUP.md"
cp "$KIT/_NEXT.md"          "$DEST/_NEXT.md"
cp "$KIT/next/_NEXT_001.md" "$DEST/next/_NEXT_001.md"

# Layer 2 — coherence maps (data half; the bin/ guards stay in <kit-dir>)
cp "$KIT/SYNC_MAP.md"       "$DEST/SYNC_MAP.md"
cp "$KIT/SYSTEM_MAP.md"     "$DEST/SYSTEM_MAP.md"

# Layer 4 — memory
cp "$KIT/memory/MEMORY.md"  "$DEST/memory/MEMORY.md"
cp "$KIT/memory/README.md"  "$DEST/memory/README.md"

# Layer 5 — ledger (clean templates) + archive
for f in session-fixes DECISIONS LESSONS audit-state drift-guard-evidence drift-guard-overfires USER_TASKS; do
  cp "$KIT/ledger/$f.md" "$DEST/ledger/$f.md"
done
cp "$KIT/_ARCHIVE/README.md" "$DEST/_ARCHIVE/README.md"

# Layer 5 — CHANGELOG: a FRESH seed. The kit's own CHANGELOG carries its
# development history — never copy it into a new project.
cat > "$DEST/ledger/CHANGELOG.md" <<EOF
# CHANGELOG — Master System Log

Append-only. Newest entries first. One \`## YYYY-MM-DD\` block per session that makes structural changes.
Small script edits or one-off fixes don't need an entry — only changes that affect how a future session understands the system.

Written by \`/handoff\` (or manually after structural edits). Do not edit existing entries.

---

## $(date +%Y-%m-%d) — project initialized via /init

Scaffolded the five-layer data root in this directory: \`_LOADUP.md\`, \`_NEXT.md\`, \`next/\` (seed \`_NEXT_001\`), \`ledger/\`, \`memory/\`, \`_ARCHIVE/\`, \`SYNC_MAP.md\` + \`SYSTEM_MAP.md\`. Machinery (commands, hooks, \`bin/\`) lives in the kit; this dir holds project data only, resolved at runtime as \`<system-dir>\`.
EOF

echo "✓ scaffolded $DEST"
```

If the guard printed `ALREADY-INIT`, stop here and tell the user the project is already initialized — do **not** run the rest of the steps.

## Step 2 — verify the scaffold boots

Run the kit's boot check against the freshly-scaffolded data root:

```bash
python3 <kit-dir>/bin/coherence-check.py --boot
```

Expect `✓ coherence-check --boot: clean`. It asserts the five required data files (`_LOADUP.md`, `_NEXT.md`, `ledger/CHANGELOG.md`, `ledger/audit-state.md`, `SYNC_MAP.md`) plus the installed `settings.json` + `CLAUDE.md`. If it flags a `MISSING` data file, a copy failed — confirm `<kit-dir>` resolved to a real path (it should be baked absolute in this command).

## Step 3 — report + hand back to the user

Emit a short confirmation, then name the two things only the user can do — don't run `/session` yourself, because the `_LOADUP.md` placeholders need their input first:

```
✓ initialized <system-dir> at <DEST>
  scaffolded: _LOADUP.md · _NEXT.md · next/_NEXT_001 · ledger/ (8) · memory/ (2) · SYNC_MAP · SYSTEM_MAP · _ARCHIVE/
  coherence-check --boot: clean

next:
  1. Fill in _LOADUP.md — replace every <fill-in>/<date> placeholder with this project's
     specifics (§0 architecture, §1 fast-path, §2 settled facts).
  2. Say svaha (or run /session) to boot the loop.
```

## What /init does NOT do

- **No machinery copies.** Commands, hooks, `bin/`, `settings.json`, `CLAUDE.md` are installed once by `setup.sh` into `~/.claude` + `<kit-dir>`. `/init` is data-only.
- **No clobber.** The `_LOADUP.md` guard makes it safe to run by mistake — it refuses rather than overwrite filled-in data.
- **No git.** Whether the project is a repo is the user's call; `/handoff` commits later if it already is one.
