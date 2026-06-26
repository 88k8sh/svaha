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

# Guard 0 — never scaffold inside the Svaha kit distribution itself (v0.6.2).
if [ -f "$DEST/.svaha-kit" ]; then
  echo "KIT-DIR: $DEST is the Svaha kit (.svaha-kit) — /init refuses. Run /init inside your own project."
  exit 0
fi

# Guard — never clobber an initialized project.
if [ -f "$DEST/_LOADUP.md" ]; then
  echo "ALREADY-INIT: $DEST/_LOADUP.md exists — /init refuses to clobber. Run /session instead."
  exit 0
fi

mkdir -p "$DEST/next" "$DEST/ledger" "$DEST/memory" "$DEST/_ARCHIVE"

# Layer 1 — handoff loop (data half)
cp "$KIT/templates/_LOADUP.template.md" "$DEST/_LOADUP.md"
cp "$KIT/_NEXT.md"                       "$DEST/_NEXT.md"
cp "$KIT/templates/_NEXT_001.md"         "$DEST/next/_NEXT_001.md"

# Fill the deterministic placeholders /init can resolve itself, so the user never
# meets them as blanks: dates (today). §0/§1 get drafted from the project in Step 2.
TODAY="$(date +%Y-%m-%d)"
tmp="$(mktemp)" && sed "s/<date>/$TODAY/g" "$DEST/_LOADUP.md" > "$tmp" && mv "$tmp" "$DEST/_LOADUP.md"

# Layer 2 — coherence maps (data half; the bin/ guards stay in <kit-dir>)
cp "$KIT/SYNC_MAP.md"       "$DEST/SYNC_MAP.md"
cp "$KIT/SYSTEM_MAP.md"     "$DEST/SYSTEM_MAP.md"

# Layer 4 — memory
cp "$KIT/memory/MEMORY.md"  "$DEST/memory/MEMORY.md"
cp "$KIT/memory/README.md"  "$DEST/memory/README.md"

# Layer 5 — ledger SEED templates + archive. Copy from templates/ledger/, NOT the kit's
# live ledger/. The kit dogfoods its own ledger — real DECISIONS, session-fixes, LESSONS,
# drift-guard logs accumulate there as Svaha is developed — so copying ledger/ would seed a
# new project with the KIT's history. templates/ledger/ holds the clean header+format seeds
# (the same fresh-seed idea as the CHANGELOG below; CHANGELOG stays inline because it injects
# a dated init entry).
for f in session-fixes DECISIONS LESSONS audit-state drift-guard-evidence drift-guard-overfires USER_TASKS EXTERNAL_DELIVERABLES; do
  cp "$KIT/templates/ledger/$f.md" "$DEST/ledger/$f.md"
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

## Step 2 — draft `_LOADUP.md` from the project (don't hand back blanks)

The scaffold copied a template whose project-specific sections (§0 architecture, §1 fast path) still read as placeholders. Fill them in now, *from the project itself*, so the user reviews a draft instead of authoring from a blank form. **Keep it bounded — do not walk the tree:** read only the project-root listing (`ls`), plus the `README` and one manifest (`package.json` / `pyproject.toml` / `go.mod` / `Cargo.toml`) if present. A few cheap reads, no recursion.

Then edit `$DEST/_LOADUP.md`:

1. **§0 (System architecture)** — replace the generic paragraph with a one-paragraph draft of what *this* project is and its top-level shape, from what you just read. If the project is empty or its shape isn't clear, keep the generic default rather than guess.
2. **§1 (the fast path)** — name the 1–3 files a session should always load (the README, a core spec). If nothing is obvious yet, keep the minimal default.
3. **Delete the `> **This is a template…**` banner line** at the top — this is a real `_LOADUP` now, not a blank form.
4. **Leave §4 (retrieval index) and §6 (on-demand) as they are** — they legitimately start sparse and fill in as the project accumulates material.

Draft, don't perfect: a rough-but-real `_LOADUP` the user skims and corrects beats an empty one they have to write from scratch.

## Step 3 — verify the scaffold boots

Run the kit's boot check against the freshly-scaffolded data root:

```bash
python3 <kit-dir>/bin/coherence-check.py --boot
```

Expect `✓ coherence-check --boot: clean`. It asserts the five required data files (`_LOADUP.md`, `_NEXT.md`, `ledger/CHANGELOG.md`, `ledger/audit-state.md`, `SYNC_MAP.md`) plus the installed `settings.json` + `CLAUDE.md`. If it flags a `MISSING` data file, a copy failed — confirm `<kit-dir>` resolved to a real path (it should be baked absolute in this command).

## Step 4 — report + hand back to the user

Emit a short confirmation. Hand back so the user can review your `_LOADUP` draft before booting — don't run `/session` yourself:

```
✓ initialized <system-dir> at <DEST>
  scaffolded: _LOADUP.md (drafted) · _NEXT.md · next/_NEXT_001 · ledger/ (9) · memory/ (2) · SYNC_MAP · SYSTEM_MAP · _ARCHIVE/
  coherence-check --boot: clean

next:
  1. Skim _LOADUP.md — I drafted §0 (architecture) and §1 (fast path) from your project;
     fix anything I got wrong. §4 / §6 fill in as you work.
  2. svaha (or run /session) to boot the loop.
```

## What /init does NOT do

- **No machinery copies.** Commands, hooks, `bin/`, `settings.json`, `CLAUDE.md` are installed once by `setup.sh` into `~/.claude` + `<kit-dir>`. `/init` is data-only.
- **No clobber.** The `_LOADUP.md` guard makes it safe to run by mistake — it refuses rather than overwrite filled-in data.
- **No git.** Whether the project is a repo is the user's call; `/handoff` commits later if it already is one.
