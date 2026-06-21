#!/usr/bin/env python3
"""
security-guard.py — PreToolUse defense-in-depth hook for Claude Code.

Blocks (or forces a confirm on) a small, high-confidence set of dangerous tool
calls BEFORE they run. Allow-by-default: it only ever acts on specific patterns,
so normal work is never touched.

  DENY (hard block — never legitimate inside an agent session):
    • reading/writing credential & secret files (~/.ssh, ~/.aws, .env, *.pem,
      tokens, keychain, .npmrc, kube config, …)
    • catastrophic shell ops (rm -rf / or ~, chmod -R 777, curl | sh, fork bomb)
  ASK (surface a confirmation — sometimes legitimate, but history-/data-losing):
    • git force-push, git reset --hard, git branch -D

Policy lives in CLAUDE.md (Privacy & guardrails + the confirmation gate). This hook
is the *enforcement* layer for the parts a machine can check deterministically — a
backstop for when a confirmation gate gets fat-fingered, not a replacement for it.

Fails OPEN on any parse error or unexpected input (exit 0). A security hook that
crashes tools is worse than one that occasionally misses.

The IDEA of a runtime guard hook is credited to mp-web3/claude-starter-kit
(github.com/mp-web3/claude-starter-kit). Independent implementation — no code reused.

Wire under PreToolUse (matcher "Bash|Edit|Write|MultiEdit|Read") in
~/.claude/settings.json:  python3 <system-dir>/bin/security-guard.py

Output follows the current Claude Code PreToolUse spec
(hookSpecificOutput.permissionDecision ∈ {"deny","ask","allow"}). If your Claude
Code predates that field it ignores the JSON and the call proceeds (fail-open) —
verify against your installed version's hook docs and adjust if needed.

SETUP: tune the pattern lists below (rows marked "# ← customize").
"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ── CONFIGURE ─────────────────────────────────────────────────────────────────
# Secret/credential path fragments — read OR write is denied.            # ← customize
SECRET_PATH_PATTERNS = [
    r"/\.ssh/", r"/\.aws/", r"/\.gnupg/", r"/\.config/gh/", r"/\.docker/config",
    r"\.env(\.|$)", r"\.pem$", r"\bid_rsa\b", r"\bid_ed25519\b",
    r"credentials", r"\bsecrets?\b", r"\.npmrc$", r"\.pypirc$",
    r"/Library/Keychains/", r"/\.kube/config", r"\.netrc$",
]
# Catastrophic bash — hard DENY (never legitimate from an agent).         # ← customize
DENY_BASH = [
    (r"\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r", "_RM_SENTINEL_"),  # refined below
    (r"\bchmod\s+-R\s+777\b", "chmod -R 777 (world-writable tree)"),
    (r"\bcurl\b[^|;&]*\|\s*(sudo\s+)?(ba)?sh\b", "curl piped straight into a shell"),
    (r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:", "fork bomb"),
    (r"\bdd\b[^\n]*\bof=/dev/(disk|sd|rdisk)", "dd to a raw disk device"),
    (r"\bmkfs\.", "filesystem format (mkfs)"),
    (r">\s*/dev/(sd|disk|rdisk)", "redirect into a raw disk device"),
]
# rm -rf aimed at / or $HOME specifically (the irreversible case).
RM_ROOT_HOME = re.compile(r"\brm\s+(-[a-zA-Z]*\s+)*-?[a-zA-Z]*\s*(-rf|-fr|-r\s+-f|-f\s+-r)\b[^\n]*\s(/|~|\$HOME|/\*)(\s|/|$)")
# History-/data-losing git — surface a confirm (ASK).                     # ← customize
ASK_BASH = [
    (r"\bgit\s+push\b[^\n]*\s(--force|-f|--force-with-lease)\b", "git force-push (rewrites remote history)"),
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard (discards uncommitted work)"),
    (r"\bgit\s+branch\s+-D\b", "git branch -D (force-delete a branch)"),
    (r"\bgit\s+clean\s+-[a-z]*f[a-z]*d|\bgit\s+clean\s+-[a-z]*d[a-z]*f", "git clean -fd (deletes untracked files)"),
]
SECRET_PATH_RE = re.compile("|".join(SECRET_PATH_PATTERNS), re.IGNORECASE)
SECRET_READ_CMD = re.compile(
    r"\b(cat|less|more|head|tail|bat|strings|xxd|od|cp|scp|rsync|base64|grep|awk|sed)\b[^\n]*?("
    + "|".join(SECRET_PATH_PATTERNS) + r")", re.IGNORECASE)
# ── END CONFIGURE ─────────────────────────────────────────────────────────────


def decide(decision, reason):
    """Emit a PreToolUse permission decision ('deny' | 'ask') and exit 0."""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": "security-guard: " + reason,
        }
    }))
    _log(decision, reason)
    sys.exit(0)


def _log(decision, reason):
    if os.environ.get("SECURITY_GUARD_NO_LOG"):
        return
    try:
        log = Path(__file__).resolve().parent.parent / "30_LEDGER" / "security-guard-log.jsonl"
        with open(log, "a") as f:
            f.write(json.dumps({
                "ts": datetime.now().isoformat(timespec="seconds"),
                "decision": decision, "reason": reason,
            }, ensure_ascii=False) + "\n")
    except Exception:
        pass  # logging is best-effort; never interfere with the tool call


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # fail open — never block on a parse error

    tool = data.get("tool_name") or ""
    ti = data.get("tool_input") or {}

    if tool == "Bash":
        cmd = ti.get("command") or ""
        if RM_ROOT_HOME.search(cmd):
            decide("deny", "rm -rf targeting / or your home directory — refused. If truly intended, run it yourself outside the agent.")
        for pat, label in DENY_BASH:
            if label == "_RM_SENTINEL_":
                continue  # handled by RM_ROOT_HOME above
            if re.search(pat, cmd):
                decide("deny", "blocked a catastrophic command (" + label + ").")
        if SECRET_READ_CMD.search(cmd):
            decide("deny", "blocked a read of a credential/secret file — secrets must not enter an agent session.")
        for pat, label in ASK_BASH:
            if re.search(pat, cmd):
                decide("ask", "confirm before " + label + ".")
        sys.exit(0)

    if tool in ("Read", "Edit", "Write", "MultiEdit"):
        fp = (ti.get("file_path") or "").replace("\\", "/")
        if fp and SECRET_PATH_RE.search(fp):
            decide("deny", "blocked access to a credential/secret file: " + fp)
        sys.exit(0)

    sys.exit(0)  # every other tool: allow (silent)


if __name__ == "__main__":
    main()
