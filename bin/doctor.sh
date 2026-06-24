#!/usr/bin/env bash
#
# Svaha — doctor: verify the install is wired up correctly.
#
# Run after setup + the settings.json merge to catch the usual silent failures
# (invalid JSON, an unreplaced <kit-dir>, a missing hook, a moved kit folder).
#
#   bash bin/doctor.sh        # from the kit root, or anywhere — it resolves itself
#
# bash 3.2 compatible. Exit 0 if all good, 1 if any check fails.

set -u

# --- resolve the kit root (this script lives in bin/, so root = its parent) ---
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$( readlink "$SOURCE" )"
  case "$SOURCE" in /*) ;; *) SOURCE="$DIR/$SOURCE" ;; esac
done
BIN_DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
KIT_ROOT="$( cd -P "$BIN_DIR/.." >/dev/null 2>&1 && pwd )"
CLAUDE_DIR="$HOME/.claude"
SETTINGS="$CLAUDE_DIR/settings.json"

fail=0
ok()   { echo "  ✓ $1"; }
warn() { echo "  – $1"; }
bad()  { echo "  ✗ $1"; echo "      → $2"; fail=$(( fail + 1 )); }

echo ""
echo "=========================================================="
echo " Svaha doctor"
echo "   kit  : $KIT_ROOT"
echo "   config: $CLAUDE_DIR"
echo "=========================================================="
echo ""

# 1 — python3 (the guard hooks are Python)
if command -v python3 >/dev/null 2>&1; then
  ok "python3 present"
else
  bad "python3 not found" "install Python 3 — the guard hooks need it"
fi

# 2 — the six slash commands
miss=""
for f in boot session handoff reflect audit foldin; do
  [ -f "$CLAUDE_DIR/commands/$f.md" ] || miss="$miss $f"
done
if [ -z "$miss" ]; then ok "6 slash commands installed"; else bad "missing commands:$miss" "re-run ./setup.sh"; fi

# 3 — the six hooks
hmiss=""
for f in context-canary launchpad-nudge memory-reflect resume-line-guard session-end-backstop session-start-marker; do
  [ -f "$CLAUDE_DIR/hooks/$f.sh" ] || hmiss="$hmiss $f"
done
if [ -z "$hmiss" ]; then ok "6 hook scripts installed"; else bad "missing hooks:$hmiss" "re-run ./setup.sh"; fi

# 4 — the kit's guard + handoff scripts (referenced by absolute path, so the folder must stay put)
bmiss=""
for f in security-guard.py version-guard.py drift-guard.py coherence-check.py next-write.sh next-live.sh; do
  [ -f "$KIT_ROOT/bin/$f" ] || bmiss="$bmiss $f"
done
if [ -z "$bmiss" ]; then ok "guard + handoff scripts present in bin/"; else bad "missing bin scripts:$bmiss" "this kit folder is incomplete — re-download"; fi

# 5 — settings.json: exists, valid JSON, no leftover placeholder, hooks wired, paths real
if [ ! -f "$SETTINGS" ]; then
  bad "no $SETTINGS" "run ./setup.sh (it can generate it) or merge settings.json.snippet"
else
  json_ok=1
  if command -v python3 >/dev/null 2>&1; then
    if ! python3 -m json.tool "$SETTINGS" >/dev/null 2>&1; then json_ok=0; fi
  fi
  if [ "$json_ok" -eq 0 ]; then
    bad "settings.json is not valid JSON" "run: python3 -m json.tool $SETTINGS   — it shows the line"
  else
    ok "settings.json is valid JSON"
    if grep -q '<kit-dir>' "$SETTINGS" 2>/dev/null; then
      bad "settings.json still has a literal <kit-dir>" "replace it with: $KIT_ROOT"
    else
      ok "no leftover <kit-dir> placeholder"
    fi
    if grep -q 'security-guard.py' "$SETTINGS" 2>/dev/null; then
      ok "guard hooks wired"
    else
      bad "guard hooks not wired in settings.json" "merge the snippet's \"hooks\" block"
    fi
    if grep -q '"permissions"' "$SETTINGS" 2>/dev/null; then
      ok "permission posture present"
    else
      warn "no \"permissions\" block (optional — you'll just be prompted per action)"
    fi
    # the wired guard path must actually exist (catches a moved kit folder)
    wired="$( grep -o 'python3 [^"]*security-guard.py' "$SETTINGS" 2>/dev/null | head -1 | sed 's/^python3 //' )"
    if [ -n "$wired" ] && [ ! -f "$wired" ]; then
      bad "settings.json points at a guard that isn't there: $wired" "the kit folder moved — re-run setup or repoint paths to $KIT_ROOT/bin"
    fi
  fi
fi

echo ""
if [ "$fail" -eq 0 ]; then
  echo "✓ All good — Svaha is wired up. Open Claude Code and run  /session"
  echo "=========================================================="
  exit 0
else
  echo "✗ $fail issue(s) above. Fix them, then re-run:  bash bin/doctor.sh"
  echo "=========================================================="
  exit 1
fi
