#!/usr/bin/env bash
#
# Throughline — turnkey installer.
#
# Makes Throughline one-flow: copies the slash commands and hooks into your
# global Claude config, then points you at the two manual steps that are too
# risky to automate (merging settings.json, installing the MCP companions).
#
# SAFETY CONTRACT:
#   - bash 3.2 compatible (macOS /bin/bash) — no mapfile, no associative arrays,
#     no `set -e` foot-guns.
#   - Non-destructive: only ever creates dirs and copies files into ~/.claude/.
#   - Never overwrites an existing ~/.claude/CLAUDE.md without a y/N prompt.
#   - Idempotent: safe to re-run; re-running just refreshes the copied files.
#
# USAGE:
#   chmod +x setup.sh   # make it executable (one time)
#   ./setup.sh          # run from anywhere — it resolves its own dir
#
# Parse-check before shipping any edit:  bash -n setup.sh

# Intentionally NOT using `set -e`: on bash 3.2 a single non-zero return from a
# benign command (e.g. a grep miss) would abort the whole install. We check
# return codes explicitly where it matters instead.
set -u

# ----------------------------------------------------------------------------
# Step 1 — Resolve this script's own directory as the kit root.
# ----------------------------------------------------------------------------
# Resolve symlinks so KIT_ROOT is the real on-disk location even if setup.sh
# was invoked via a symlink. bash-3.2-safe (no realpath dependency).
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$( readlink "$SOURCE" )"
  case "$SOURCE" in
    /*) ;;                       # absolute symlink target — use as-is
    *) SOURCE="$DIR/$SOURCE" ;;  # relative target — resolve against link dir
  esac
done
KIT_ROOT="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"

CLAUDE_DIR="$HOME/.claude"
CMD_DIR="$CLAUDE_DIR/commands"
HOOK_DIR="$CLAUDE_DIR/hooks"

echo ""
echo "=========================================================="
echo " Throughline installer"
echo "=========================================================="
echo "Step 1/6  Kit root resolved:"
echo "          $KIT_ROOT"
echo ""

# ----------------------------------------------------------------------------
# Step 2 — Copy the six slash commands to ~/.claude/commands/
# ----------------------------------------------------------------------------
echo "Step 2/6  Installing slash commands -> $CMD_DIR"
mkdir -p "$CMD_DIR"

COMMANDS="boot.md session.md handoff.md reflect.md audit.md foldin.md"
cmd_ok=0
cmd_miss=0
for f in $COMMANDS; do
  if [ -f "$KIT_ROOT/$f" ]; then
    cp "$KIT_ROOT/$f" "$CMD_DIR/$f"
    echo "          copied  $f"
    cmd_ok=$((cmd_ok + 1))
  else
    echo "          MISSING $f  (not found in kit root — skipped)"
    cmd_miss=$((cmd_miss + 1))
  fi
done
echo "          done ($cmd_ok copied, $cmd_miss missing)"
echo ""

# ----------------------------------------------------------------------------
# Step 3 — Copy hooks/*.sh to ~/.claude/hooks/
# ----------------------------------------------------------------------------
echo "Step 3/6  Installing hooks -> $HOOK_DIR"
mkdir -p "$HOOK_DIR"

hook_ok=0
if [ -d "$KIT_ROOT/hooks" ]; then
  # Glob expands in-place; guard against the literal-glob case when empty.
  for f in "$KIT_ROOT"/hooks/*.sh; do
    [ -f "$f" ] || continue
    base="$( basename "$f" )"
    cp "$f" "$HOOK_DIR/$base"
    # Some hooks (e.g. session-end-backstop.sh) embed a <system-dir> placeholder
    # they need to resolve the kit's next/ dir from ~/.claude/hooks/, where the
    # in-kit ../next fallback no longer applies. Rewrite it to the real root.
    if grep -q '<system-dir>' "$HOOK_DIR/$base" 2>/dev/null; then
      sed "s|<system-dir>|$KIT_ROOT|g" "$HOOK_DIR/$base" > "$HOOK_DIR/$base.tmp" \
        && mv "$HOOK_DIR/$base.tmp" "$HOOK_DIR/$base"
      echo "          copied  $base  (rewrote <system-dir> -> $KIT_ROOT)"
    else
      echo "          copied  $base"
    fi
    chmod +x "$HOOK_DIR/$base" 2>/dev/null
    hook_ok=$((hook_ok + 1))
  done
fi
if [ "$hook_ok" -eq 0 ]; then
  echo "          no .sh hooks found in $KIT_ROOT/hooks (nothing copied)"
else
  echo "          done ($hook_ok hooks copied, +x set)"
fi
echo ""

# ----------------------------------------------------------------------------
# Step 3b — Optional CLAUDE.md install (NEVER overwrite without asking).
# ----------------------------------------------------------------------------
# The kit ships a template CLAUDE.md. Offer to drop it at ~/.claude/CLAUDE.md,
# but if one already exists we MUST NOT clobber it without explicit consent.
if [ -f "$KIT_ROOT/CLAUDE.md" ]; then
  TARGET_CLAUDE="$CLAUDE_DIR/CLAUDE.md"
  if [ -f "$TARGET_CLAUDE" ]; then
    echo "          NOTE: $TARGET_CLAUDE already exists."
    printf "          Overwrite it with the kit's CLAUDE.md template? [y/N] "
    read REPLY
    case "$REPLY" in
      y|Y|yes|YES)
        cp "$TARGET_CLAUDE" "$TARGET_CLAUDE.backup.$( date +%Y%m%d-%H%M%S )"
        cp "$KIT_ROOT/CLAUDE.md" "$TARGET_CLAUDE"
        echo "          overwrote (a timestamped .backup was kept alongside it)"
        ;;
      *)
        echo "          kept your existing CLAUDE.md (no change)"
        ;;
    esac
  else
    cp "$KIT_ROOT/CLAUDE.md" "$TARGET_CLAUDE"
    echo "          installed CLAUDE.md template -> $TARGET_CLAUDE"
  fi
  echo ""
fi

# ----------------------------------------------------------------------------
# Step 4 — Point the user at the settings.json merge (do NOT auto-edit it).
# ----------------------------------------------------------------------------
# Editing a user's settings.json programmatically risks corrupting JSON they
# rely on. We print the snippet path + the placeholder they must replace, and
# stop. The merge is a deliberate manual step.
echo "Step 4/6  Wire up the hooks via settings.json (MANUAL — not auto-edited)"
echo "          Merge this snippet into your settings:"
echo "            snippet : $KIT_ROOT/settings.json.snippet"
echo "            target  : $CLAUDE_DIR/settings.json"
echo "          In the snippet, replace every <system-dir> placeholder with"
echo "          your system root (the folder holding bin/, next/, 30_LEDGER/)."
echo "          For this kit that absolute path is:"
echo "            $KIT_ROOT"
echo "          (The ~/.claude/hooks/* paths in the snippet are literal —"
echo "           leave them as-is.) If you already have a \"hooks\" key, merge"
echo "          per-event (PreToolUse / PostToolUse / Stop), don't replace it."
echo ""

# ----------------------------------------------------------------------------
# Step 5 — Optional companions (print only — install knowingly, by hand).
# ----------------------------------------------------------------------------
# Throughline never auto-installs a third party or reads an API key. These are
# the canonical install lines; run the one you want yourself. See README / CREDITS.
echo "Step 5/6  Optional companions (install yourself — not auto-run)"
echo "          Context7 (up-to-date library docs, MCP) — run in your SHELL"
echo "          (a free key at context7.com lifts rate limits; the no-key form also works):"
echo "            claude mcp add --scope user context7 -- npx -y @upstash/context7-mcp --api-key YOUR_API_KEY"
echo "          Superpowers (engineering-skill methodology) — paste in a Claude Code session:"
echo "            /plugin install superpowers@claude-plugins-official"
echo ""

# ----------------------------------------------------------------------------
# Step 6 — How to start.
# ----------------------------------------------------------------------------
echo "Step 6/6  All set."
echo "          To start: open Claude Code and run  /session"
echo "=========================================================="
echo ""
