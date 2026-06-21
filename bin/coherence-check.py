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

# Root of your project (the folder containing _NEXT.md, _LOADUP.md, etc.)
SYSTEM_DIR = Path("<system-dir>")           # ← CHANGE THIS to an absolute path to your project root

# Where your Claude slash commands live (real Claude Code location — leave as-is)
DOT_CLAUDE = HOME / ".claude"
COMMANDS_DIR = DOT_CLAUDE / "commands"

CHANGELOG = SYSTEM_DIR / "30_LEDGER" / "CHANGELOG.md"
AUDIT_STATE = SYSTEM_DIR / "30_LEDGER" / "audit-state.md"
NEXT_DIR = SYSTEM_DIR / "next"

# Slash commands _LOADUP §2 declares as registered (stems only, no .md).
REGISTERED_COMMANDS = {
    "boot", "session", "handoff", "foldin", "reflect", "audit",
    # add yours here
}

# Mirror drift-guard.py's structural-file scope.
PLUMBING_FILES = [
    SYSTEM_DIR / "CLAUDE.md",
    SYSTEM_DIR / "_LOADUP.md",
    SYSTEM_DIR / "_NEXT.md",
    SYSTEM_DIR / "SYNC_MAP.md",
    SYSTEM_DIR / "SYSTEM_MAP.md",
    DOT_CLAUDE / "settings.json",
    # add your project's structural files here
]
# Add all command files and bin scripts dynamically.
PLUMBING_DIRS = [
    (COMMANDS_DIR, "*.md"),
    (SYSTEM_DIR / "bin", "*.py"),
    (SYSTEM_DIR / "bin", "*.sh"),
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
        SYSTEM_DIR / "CLAUDE.md",
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
