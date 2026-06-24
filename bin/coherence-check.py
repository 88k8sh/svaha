#!/usr/bin/env python3
"""
coherence-check.py — structural integrity checker for context-management systems.

Two modes:
  --boot   Structural integrity check. Claude runs this via Bash at boot; reads stdout.
  --stop   Stop-hook exit check. Wired in settings.json Stop hooks; outputs systemMessage JSON.

Boot checks:
  1. Required plumbing files exist.
  2. Slash commands in ~/.claude/commands/ match the REGISTERED_COMMANDS list below.
  3. audit-state.md is readable.

Stop checks:
  1. Any plumbing file modified more recently than CHANGELOG.md → flag by name.
     (Catches: "you edited X but forgot to log it.")
  2. Delta (_NEXT high-water − last_audit_next) ≥ 5 → nudge toward /audit.
  Silent if clean. Fires once per session (sentinel-gated).

SETUP: Edit the constants below to match your project layout before use.
"""

import json
import os
import re
import sys
from pathlib import Path

# ── CONFIGURE THESE FOR YOUR PROJECT ──────────────────────────────────────────

HOME = Path.home()

# Kit root — where this script and the rest of bin/ live. Resolved from __file__,
# never baked, so the check works no matter where the kit was cloned.
KIT_DIR = Path(__file__).resolve().parent.parent


def discover_system_dir():
    """The per-project data root — the dir holding _LOADUP.md — found by a bounded
    search around the launch CWD (this hook is global; it fires in every project, so
    nothing is hand-edited):
      1. up-scan: CWD then its ancestors (covers launch *inside* the system or below it);
      2. down-scan: CWD's immediate children, if exactly one holds a _LOADUP.md (covers
         launch in a *workspace that contains* the system — the nested layout — where the
         system sits one level below CWD). Ambiguous (2+) or none → fall through.
    Bounded both ways (ancestors + one level down) — never a recursive walk, so it can't
    trigger the filesystem-exploration storm. Falls back to KIT_DIR, which doubles as its
    own system dir in a combined repo, so a run from inside the kit still works."""
    try:
        start = Path.cwd().resolve()
    except Exception:
        return KIT_DIR
    # 1. up-scan — CWD and ancestors. Anchor must be a regular FILE (.is_file(), not
    #    .exists()) so a dir named _LOADUP.md is rejected — matches the shell hooks' `-f`.
    for cand in [start, *start.parents]:
        if (cand / "_LOADUP.md").is_file():
            return cand
    # 2. down-scan — immediate children only, unambiguous match only. Dedup by RESOLVED
    #    real path so a symlink twin (myproj/ + current->myproj) counts once, not as a
    #    false ambiguity; a genuine 2nd system still resolves to a distinct real path.
    try:
        kids = {c.resolve() for c in start.iterdir()
                if c.is_dir() and not c.name.startswith(".") and (c / "_LOADUP.md").is_file()}
    except Exception:
        kids = set()
    if len(kids) == 1:
        return next(iter(kids))
    # 3. not found — fall back to the kit (combined-repo / self-check default)
    return KIT_DIR


# Project data root (next/, ledger/, _LOADUP.md, …) — per-project, runtime-resolved.
SYSTEM_DIR = discover_system_dir()

# Where your Claude slash commands + installed config live (real Claude Code location).
DOT_CLAUDE = HOME / ".claude"
COMMANDS_DIR = DOT_CLAUDE / "commands"

CHANGELOG = SYSTEM_DIR / "ledger" / "CHANGELOG.md"
AUDIT_STATE = SYSTEM_DIR / "ledger" / "audit-state.md"
NEXT_DIR = SYSTEM_DIR / "next"

# Slash commands _LOADUP §2 declares as registered (stems only, no .md).
REGISTERED_COMMANDS = {
    "boot", "session", "handoff", "foldin", "reflect", "audit",
    # add yours here
}

# Mirror drift-guard.py's structural-file scope. Each file is listed at every
# location it can live — data files in SYSTEM_DIR, installed config in ~/.claude,
# the combined-repo CLAUDE.md at the system root — and all_plumbing() existence-
# filters, so a candidate that isn't present is simply skipped.
PLUMBING_FILES = [
    DOT_CLAUDE / "CLAUDE.md",
    SYSTEM_DIR / "CLAUDE.md",
    SYSTEM_DIR / "_LOADUP.md",
    SYSTEM_DIR / "_NEXT.md",
    SYSTEM_DIR / "SYNC_MAP.md",
    SYSTEM_DIR / "SYSTEM_MAP.md",
    DOT_CLAUDE / "settings.json",
]
# Command files (installed in ~/.claude) + bin scripts (in the kit).
PLUMBING_DIRS = [
    (COMMANDS_DIR, "*.md"),
    (KIT_DIR / "bin", "*.py"),
    (KIT_DIR / "bin", "*.sh"),
]

# ── END CONFIGURATION ──────────────────────────────────────────────────────────


def all_plumbing():
    paths = list(PLUMBING_FILES)
    for d, pat in PLUMBING_DIRS:
        if d.is_dir():
            paths.extend(d.glob(pat))
    return [p for p in paths if p.exists()]


def highest_next_number():
    if not NEXT_DIR.is_dir():
        return None
    nums = []
    for f in NEXT_DIR.glob("_NEXT_*.md"):
        m = re.search(r"_NEXT_(\d+)\.md$", f.name)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) if nums else None


def parse_audit_state():
    if not AUDIT_STATE.exists():
        return None
    text = AUDIT_STATE.read_text()
    m = re.search(r"last_audit_next:\s*(\d+)", text)
    return int(m.group(1)) if m else None


# ── BOOT MODE ──────────────────────────────────────────────────────────────────

def boot():
    issues = []

    # 1. Required plumbing files exist.
    required = [
        SYSTEM_DIR / "_LOADUP.md",
        SYSTEM_DIR / "_NEXT.md",
        CHANGELOG,
        AUDIT_STATE,
        SYSTEM_DIR / "SYNC_MAP.md",
        DOT_CLAUDE / "settings.json",
    ]
    for p in required:
        if not p.exists():
            issues.append(f"MISSING: {p}")
    # CLAUDE.md lives at ~/.claude (installed) or the system root (combined repo) — either is fine.
    if not (DOT_CLAUDE / "CLAUDE.md").exists() and not (SYSTEM_DIR / "CLAUDE.md").exists():
        issues.append(f"MISSING: CLAUDE.md (looked in {DOT_CLAUDE} and {SYSTEM_DIR})")

    # 2. Slash commands: on-disk vs registered list.
    if COMMANDS_DIR.is_dir():
        on_disk = {f.stem for f in COMMANDS_DIR.glob("*.md")}
        unregistered = on_disk - REGISTERED_COMMANDS
        missing = REGISTERED_COMMANDS - on_disk
        if unregistered:
            issues.append(f"Commands on disk not in REGISTERED_COMMANDS list: {sorted(unregistered)} — update coherence-check.py")
        if missing:
            issues.append(f"Commands in REGISTERED_COMMANDS not on disk: {sorted(missing)} — missing command file")
    else:
        issues.append(f"MISSING commands dir: {COMMANDS_DIR}")

    # 3. audit-state readable.
    last_next = parse_audit_state()
    if last_next is None:
        issues.append(f"audit-state.md missing or unparseable: {AUDIT_STATE}")

    if issues:
        print("⚠ coherence-check --boot: issues found")
        for i in issues:
            print(f"  • {i}")
    else:
        print("✓ coherence-check --boot: clean")


# ── STOP MODE ──────────────────────────────────────────────────────────────────

def stop():
    # Read session_id for sentinel (stdin may have Stop hook JSON).
    try:
        data = json.load(sys.stdin)
        sid = data.get("session_id", "unknown")
        tp = data.get("transcript_path", "")
        # Size gate: skip tiny sessions.
        if tp and os.path.exists(tp):
            size = os.path.getsize(tp)
            if size < 5000:
                sys.exit(0)
    except Exception:
        sid = "unknown"
        tp = ""

    # Sentinel: fire once per session.
    sentinel = Path(os.environ.get("TMPDIR", "/tmp")) / f"claude-coherence-stop-{sid}"
    if sentinel.exists():
        sys.exit(0)
    sentinel.touch()

    warnings = []

    # 1. Plumbing files newer than CHANGELOG.
    if CHANGELOG.exists():
        changelog_mtime = CHANGELOG.stat().st_mtime
        for p in all_plumbing():
            if p.resolve() == CHANGELOG.resolve():
                continue
            if p.stat().st_mtime > changelog_mtime:
                rel = p.relative_to(HOME) if HOME in p.parents else p
                warnings.append(f"{rel} edited but CHANGELOG not updated after it")

    # 2. Audit nudge.
    high = highest_next_number()
    last = parse_audit_state()
    if high is not None and last is not None:
        delta = high - last
        if delta >= 5:
            warnings.append(
                f"/audit nudge: {delta} _NEXT files since last audit (_NEXT_{last:03d}→_NEXT_{high:03d})"
            )

    if not warnings:
        sys.exit(0)

    msg = "⚠ coherence-check at session end:\n" + "\n".join(f"  • {w}" for w in warnings)
    print(json.dumps({"systemMessage": msg}))


# ── ENTRY ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--boot"
    if mode == "--stop":
        stop()
    else:
        boot()
