#!/usr/bin/env bash
#
# Svaha — turnkey installer.
#
# Makes Svaha one-flow: copies the slash commands and hooks into your
# global Claude config, offers to generate settings.json for you (only if you
# don't already have one, and only with consent), and points you at the optional
# MCP companions. Verify the result anytime with: bash bin/doctor.sh
#
# SAFETY CONTRACT:
#   - bash 3.2 compatible (macOS /bin/bash) — no mapfile, no associative arrays,
#     no `set -e` foot-guns.
#   - Non-destructive: creates dirs + copies files; writes settings.json ONLY with
#     a y/N prompt and ONLY if absent — never clobbers an existing settings.json.
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
echo " Svaha installer"
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
# Step 4 — Wire up settings.json. Offer to generate it (with consent); NEVER
#          clobber an existing one.
# ----------------------------------------------------------------------------
# Auto-editing a user's EXISTING settings.json risks corrupting JSON they rely
# on — so we only ever write a fresh one (behind a y/N prompt), or, if one
# already exists, produce a placeholder-filled, JSON-validated copy to merge.
echo "Step 4/6  Wire up the hooks + permissions via settings.json"
SNIPPET="$KIT_ROOT/settings.json.snippet"
TARGET_SETTINGS="$CLAUDE_DIR/settings.json"

# Strip the // comment header, substitute <system-dir>, validate JSON; write to $1.
# Returns non-zero (and cleans up the temp) on any failure — never leaves a half file.
gen_settings() {
  local out tmp
  out="$1"; tmp="$out.tmp.$$"
  sed '/^[[:space:]]*\/\//d' "$SNIPPET" 2>/dev/null | sed "s|<system-dir>|$KIT_ROOT|g" > "$tmp" 2>/dev/null || { rm -f "$tmp"; return 1; }
  if command -v python3 >/dev/null 2>&1; then
    python3 -m json.tool "$tmp" >/dev/null 2>&1 || { rm -f "$tmp"; return 1; }
  fi
  mv "$tmp" "$out"
}

if [ ! -f "$SNIPPET" ]; then
  echo "          (settings.json.snippet not found in kit — skipping)"
elif [ -f "$TARGET_SETTINGS" ]; then
  # Existing settings — never touch them. Hand over a ready-to-merge copy.
  GEN="$KIT_ROOT/settings.generated.json"
  if gen_settings "$GEN"; then
    echo "          You already have $TARGET_SETTINGS — leaving it untouched."
    echo "          Wrote a ready-to-merge copy (path filled in, JSON-validated):"
    echo "            $GEN"
    echo "          Merge its \"permissions\" + \"hooks\" blocks into your settings.json"
    echo "          (per-array / per-event if you already have those keys)."
  else
    echo "          Couldn't build the merge file — merge $SNIPPET by hand"
    echo "          (replace <system-dir> with $KIT_ROOT)."
  fi
else
  # No settings.json yet — offer to generate it.
  echo "          No $TARGET_SETTINGS yet."
  printf "          Generate it now (fills in the path, validates the JSON)? [y/N] "
  read REPLY
  case "$REPLY" in
    y|Y|yes|YES)
      mkdir -p "$CLAUDE_DIR"
      if gen_settings "$TARGET_SETTINGS"; then
        echo "          wrote $TARGET_SETTINGS  (<system-dir> -> $KIT_ROOT, JSON valid)"
        echo "          Edit mode A (edits granted once) is the default — see the"
        echo "          snippet header to switch to per-session before first use."
      else
        echo "          generation failed (python3 missing, or unexpected) — merge"
        echo "          $SNIPPET by hand instead (replace <system-dir> with $KIT_ROOT)."
      fi
      ;;
    *)
      echo "          skipped — merge $SNIPPET into $TARGET_SETTINGS yourself"
      echo "          (replace <system-dir> with $KIT_ROOT)."
      ;;
  esac
fi
echo ""

# ----------------------------------------------------------------------------
# Step 5 — Optional companions (print only — install knowingly, by hand).
# ----------------------------------------------------------------------------
# Svaha never auto-installs a third party or reads an API key. These are
# the canonical install lines; run the one you want yourself. See README / CREDITS.
echo "Step 5/6  Optional companions (install yourself — not auto-run)"
echo "          Context7 (up-to-date library docs, MCP) — run in your SHELL"
echo "          (a free key at context7.com lifts rate limits; the no-key form also works):"
echo "            claude mcp add --scope user context7 -- npx -y @upstash/context7-mcp --api-key YOUR_API_KEY"
echo "          Superpowers (engineering-skill methodology) — paste in a Claude Code session:"
echo "            /plugin install superpowers@claude-plugins-official"
echo ""

# ----------------------------------------------------------------------------
# Step 6 — The send-off.
# ----------------------------------------------------------------------------
echo "Step 6/6  So be it."
echo ""
echo "          Verify:  bash $KIT_ROOT/bin/doctor.sh"
echo "          Begin:   open Claude Code and say  svaha   (or run /session)"
echo "=========================================================="
echo ""
