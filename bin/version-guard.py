#!/usr/bin/env python3
"""
version-guard.py — PreToolUse hook for Edit | Write | MultiEdit

HARD-BLOCKS edits to frozen artifacts. This is the *enforcement* layer for the
principle "frozen artifacts must be versioned/replaced, never silently edited."
drift-guard.py only WARNS when a frozen _NEXT_NNN.md is touched (it injects a
nudge and lets the edit through); this hook DENIES the edit outright.

  DENY (hard block):
    • file_path matching /_NEXT_NNN.md$ — frozen numbered handoffs (treat each
      like a commit; corrections go in a NEW numbered file via bin/next-write.sh).
    • any existing target whose first ~20 lines carry a YAML frontmatter line
      `frozen: true` — bump the version / write a new file instead.

Allow-by-default: it only ever acts on those two patterns, so normal work is
never touched. Fails OPEN on any parse error or unreadable input (exit 0) — a
guard that crashes tools is worse than one that occasionally misses.

The IDEA of pinning/versioning a frozen artifact at edit-time is credited to
TheDecipherist/claude-code-mastery-project-starter-kit's `check-mdd-version`
pattern (github.com/TheDecipherist/claude-code-mastery-project-starter-kit).
Independent implementation — no code reused.

Wire under PreToolUse (matcher "Edit|Write|MultiEdit") in ~/.claude/settings.json:
  python3 <kit-dir>/bin/version-guard.py

Output follows the current Claude Code PreToolUse spec
(hookSpecificOutput.permissionDecision = "deny"). If your Claude Code predates
that field it ignores the JSON and the call proceeds (fail-open) — verify against
your installed version's hook docs and adjust if needed.

Every block is appended to ledger/version-guard-log.jsonl (best-effort, never
raises). Set VERSION_GUARD_NO_LOG=1 when testing by hand so test blocks don't
pollute the log.
"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Frozen numbered handoffs — /_NEXT_<digits>.md
FROZEN_NEXT_RE = re.compile(r"/_NEXT_\d+\.md$")
# A YAML frontmatter line declaring the file frozen, e.g. `frozen: true`.
# Tolerant of leading whitespace, quotes, and trailing comments.
FRONTMATTER_FROZEN_RE = re.compile(
    r"""^\s*frozen\s*:\s*['"]?true['"]?\s*(#.*)?$""", re.IGNORECASE
)
FRONTMATTER_SCAN_LINES = 20


def deny(reason):
    """Emit a PreToolUse 'deny' decision and exit 0."""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "version-guard: " + reason,
        }
    }))
    _log(reason)
    sys.exit(0)


def _log(reason):
    if os.environ.get("VERSION_GUARD_NO_LOG"):
        return
    try:
        log = Path(__file__).resolve().parent.parent / "ledger" / "version-guard-log.jsonl"
        with open(log, "a") as f:
            f.write(json.dumps({
                "ts": datetime.now().isoformat(timespec="seconds"),
                "decision": "deny",
                "reason": reason,
            }, ensure_ascii=False) + "\n")
    except Exception:
        pass  # logging is best-effort; never interfere with the tool call


def _is_marked_frozen(file_path):
    """True if the file exists and one of its first ~20 lines is `frozen: true`
    in a YAML frontmatter sense. Best-effort: an unreadable/absent file is not
    frozen (fail open)."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f):
                if i >= FRONTMATTER_SCAN_LINES:
                    break
                if FRONTMATTER_FROZEN_RE.match(line.rstrip("\n")):
                    return True
    except Exception:
        return False  # can't read it → can't be sure it's frozen → allow
    return False


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # fail open — never block on a parse error

    tool = data.get("tool_name") or ""
    if tool not in ("Edit", "Write", "MultiEdit"):
        sys.exit(0)  # only act on edit-shaped tools

    ti = data.get("tool_input") or {}
    fp = ti.get("file_path") or ""
    p = fp.replace("\\", "/")
    if not p:
        sys.exit(0)

    # 1) Frozen numbered handoffs — block by path, no file read needed.
    if FROZEN_NEXT_RE.search(p):
        deny("frozen handoff — never edit; mint a new numbered file via bin/next-write.sh")

    # 2) Any existing target marked `frozen: true` in its frontmatter.
    if _is_marked_frozen(fp):
        deny("marked frozen: true — bump the version / write a new file instead of editing in place")

    sys.exit(0)  # everything else: allow (silent)


if __name__ == "__main__":
    main()
